import time
import numpy as np
from typing import List, Dict, Any, Callable
from app.models.customer import Customer
from app.models.depot import Depot
from app.models.vehicle import VehicleConfig
from app.services.qaoa_solver import solve_quantum
from app.services.ortools_solver import solve_classical
from validators import validate_solution

def run_benchmark_iteration(
    depot: Depot, 
    customers: List[Customer], 
    fleet: VehicleConfig, 
    solver: str
) -> Dict[str, Any]:
    
    start_time = time.perf_counter()
    
    try:
        if solver == "quantum":
            # Using qaoa_solver
            res = solve_quantum(depot, customers, fleet, bypass_clustering=False)
            dist = res.total_distance_km
            routes = res.routes
            feasible = res.feasible
        else:
            # Using ortools
            res = solve_classical(depot, customers, fleet)
            routes = res.routes
            dist = res.total_distance_km
            feasible = True
            
        runtime = time.perf_counter() - start_time
        
        if not feasible:
            status = "INFEASIBLE"
            # Use the structured reason code if available
            reason = getattr(res, "infeasible_reason", None) or "Solver safely reported Infeasible."
            errors = [reason]
        else:
            errors = validate_solution(routes, customers, fleet, dist)
            status = "FAIL" if errors else "PASS"
            
        return {
            "runtime": runtime,
            "distance": dist,
            "routes": routes,
            "status": status,
            "errors": errors
        }
    except Exception as e:
        runtime = time.perf_counter() - start_time
        return {
            "runtime": runtime,
            "distance": float('inf'),
            "routes": [],
            "status": "FAIL",
            "errors": [str(e)]
        }

def run_stability_test(
    depot: Depot, 
    customers: List[Customer], 
    fleet: VehicleConfig,
    iterations: int = 5
) -> Dict[str, Any]:
    
    distances = []
    runtimes = []
    
    for _ in range(iterations):
        res = run_benchmark_iteration(depot, customers, fleet, "quantum")
        distances.append(res["distance"])
        runtimes.append(res["runtime"])
        
    valid_dists = [d for d in distances if d != float('inf')]
    
    return {
        "name": f"Stability N={len(customers)}",
        "dist_var": np.var(valid_dists) if valid_dists else 0,
        "time_var": np.var(runtimes),
        "dist_mean": np.mean(valid_dists) if valid_dists else 0,
        "success_rate": len(valid_dists) / iterations
    }
