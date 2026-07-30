import time
import logging
from typing import List, Optional
import numpy as np

from app.models.customer import Customer
from app.models.depot import Depot
from app.models.vehicle import VehicleConfig
from app.services.base_solver import BaseQuantumSolver
from app.services.quantum_result import QuantumResult
from app.services.distance import build_distance_matrix
from app.services.fitness import evaluate_cvrp_fitness
from app.services.repair import validate_routes

logger = logging.getLogger(__name__)

class BQPhySolver(BaseQuantumSolver):
    def solve(
        self,
        depot: Depot,
        customers: List[Customer],
        vehicle_config: VehicleConfig,
        bypass_clustering: bool = False,
    ) -> QuantumResult:
        
        # 1. Prepare dynamic inputs based on len(customers) and VehicleConfig
        dist_matrix = build_distance_matrix(depot, customers)
        K = vehicle_config.total_count
        num_nodes = len(customers) + 1  # Depot + customers
        num_vehicles = K
        num_vars = num_vehicles * num_nodes * num_nodes
        
        # Build Demands array (depot is 0)
        demands = np.zeros(num_nodes)
        for i, c in enumerate(customers):
            demands[i + 1] = c.demand
            
        # For simplicity, we assume a uniform vehicle capacity in this abstraction, 
        # or take the max/average.
        vehicle_capacity = max(vehicle_config.capacities_list) if vehicle_config.capacities_list else 0.0

        t0 = time.perf_counter()

        # 2. Try importing BQPhy
        try:
            import bqphy.BQPhy_Optimiser as qea
        except ImportError as e:
            logger.error(f"BQPhy is not installed or failed to import: {e}")
            # Raise a clean exception to be handled by the caller/FastAPI
            raise RuntimeError("BQPhy solver is configured but the bqphy package is not available.") from e

        # 3. Import dynamic config
        from app import config
        
        optimizer_config = {
            "numPopulation": getattr(config, "BQPHY_POPULATION", 200),
            "maxGeneration": getattr(config, "BQPHY_GENERATIONS", 800),
            "deltaTheta": getattr(config, "BQPHY_DELTA_THETA", 0.12),
            "designVariables": num_vars,
            "typeOfOptimisation": "BINARY",
            "populationInitialSeeding": False,
            "outputFilePath": "bqphy_solver_output",
            "generationLogging": "noLogging",
        }
        
        try:
            optimizer = qea.BQPhy_OPTIMISER()
            optimizer.initialize(optimizer_config)
            
            # Closure for fitness to inject dynamic arrays
            def fitness_closure(x_batch):
                return evaluate_cvrp_fitness(
                    x_batch,
                    distance_matrix=dist_matrix,
                    demands=demands,
                    vehicle_capacity=vehicle_capacity,
                    num_vehicles=num_vehicles,
                    num_nodes=num_nodes
                )
                
            optimizer.model(fitness_closure)
            optimizer.runOptimization()
            
            best_vector, best_fitness = optimizer.getBestDesign()
            
        except Exception as e:
            logger.error(f"BQPhy execution failed: {e}")
            raise RuntimeError(f"BQPhy execution failed: {e}") from e
            
        rt = time.perf_counter() - t0
        
        # 4. Decode the result vector into routes
        X = np.round(best_vector).reshape(num_vehicles, num_nodes, num_nodes).astype(int)
        routes = []
        for k in range(num_vehicles):
            arcs = []
            for i in range(num_nodes):
                for j in range(num_nodes):
                    if X[k, i, j] == 1:
                        arcs.append((i, j))
            
            if not arcs:
                routes.append([0, 0])
                continue
                
            current_node = 0
            tour = [0]
            step = 0
            while step < num_nodes + 2:
                next_nodes = [j for (i, j) in arcs if i == current_node]
                if not next_nodes:
                    break
                next_node = next_nodes[0]
                tour.append(next_node)
                current_node = next_node
                step += 1
                if current_node == 0 and len(tour) > 1:
                    break
            
            # Ensure proper bookends
            if not tour or tour[0] != 0:
                tour.insert(0, 0)
            if tour[-1] != 0:
                tour.append(0)
                
            routes.append(tour)

        if not routes:
            routes = [[0, 0]]
            
        # Total distance
        total_km = sum(dist_matrix[a][b] for r in routes for a, b in zip(r, r[1:]))
        
        # Validation
        feasible, _ = validate_routes(routes, customers, vehicle_config.capacities_list)
        
        return QuantumResult(
            routes=routes,
            total_distance_km=round(float(total_km), 3),
            runtime_s=round(rt, 4),
            feasible=feasible,
            fallback_used=False,
            objective_best=round(float(best_fitness), 4),
            objective_mean=round(float(best_fitness), 4),
            objective_variance=0.0,
            runs=1,
            n_vars=num_vars,
            method="bqphy",
            distance_matrix=dist_matrix,
            infeasible_reason=None if feasible else "ROUTE_VALIDATION_FAILED"
        )
