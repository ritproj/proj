#!/usr/bin/env python3
"""
Step 3: Pure Quantum-Inspired Miniature CVRP (Capacitated Vehicle Routing Problem)
Problem Instance:
- 1 Depot (Node 0)
- 4 Customers (Nodes 1, 2, 3, 4)
- 2 Vehicles (Vehicle 0, Vehicle 1)
- Vehicle Capacity: 15 units each

Binary Decision Encoding:
x[k, i, j] in {0, 1} where x[k, i, j] = 1 if Vehicle k travels directly from location i to location j.
Total binary decision variables: 2 vehicles * 5 locations * 5 locations = 50 binary variables.
"""

import sys
import numpy as np
import bqphy.BQPhy_Optimiser as qea

# =============================================================================
# 1. PROBLEM GEOMETRY & DEMAND DATA
# =============================================================================
NUM_VEHICLES = 2
NUM_NODES = 5  # Node 0 = Depot, Nodes 1..4 = Customers
NUM_CUSTOMERS = 4
NUM_VARIABLES = NUM_VEHICLES * NUM_NODES * NUM_NODES  # 2 * 5 * 5 = 50 binary variables

# 2D Coordinates (Depot at (0,0), Customers in North-East & South-West clusters)
NODE_COORDS = np.array([
    [0.0, 0.0],    # Node 0: Depot
    [2.0, 3.0],    # Node 1: North-East Customer (Demand: 5)
    [3.0, 4.0],    # Node 2: North-East Customer (Demand: 7)
    [-3.0, -2.0],  # Node 3: South-West Customer (Demand: 6)
    [-4.0, -3.0],  # Node 4: South-West Customer (Demand: 8)
])  # shape: (5, 2)

# Compute Euclidean Distance Matrix D[i, j]
diff = NODE_COORDS[:, np.newaxis, :] - NODE_COORDS[np.newaxis, :, :]  # shape: (5, 5, 2)
DISTANCE_MATRIX = np.linalg.norm(diff, axis=2)  # shape: (5, 5)

# Customer Demands (Depot demand is 0)
DEMANDS = np.array([0, 5, 7, 6, 8])  # shape: (5,)
VEHICLE_CAPACITY = 15.0  # Max capacity per vehicle

# Penalty Scaling Factors
P_VISIT = 15000.0     # High barrier penalty for unvisited/multi-visited customer
P_FLOW = 15000.0      # Penalty for flow conservation (inflow != outflow)
P_CAPACITY = 8000.0   # Penalty for exceeding vehicle capacity
P_SUBTOUR = 15000.0   # Penalty for isolated cycles disconnected from depot
P_SELF_LOOP = 30000.0 # Penalty for self-loops (i -> i)


# =============================================================================
# 2. VECTORIZED FITNESS EVALUATION CALLBACK
# =============================================================================
def evaluate_cvrp_fitness(x_batch):
    """
    Vectorized CVRP Fitness Evaluation Callback.
    
    Args:
        x_batch (np.ndarray): 2D matrix of shape (numPopulation, 50)
                             where 50 = NUM_VEHICLES * NUM_NODES * NUM_NODES.
                             
    Returns:
        np.ndarray: 1D fitness array of shape (numPopulation,) to be MINIMIZED.
    """
    num_pop = x_batch.shape[0]
    
    # Reshape (num_pop, 50) into 4D tensor X: (Candidate_pop, Vehicle_k, From_i, To_j)
    X = x_batch.reshape(num_pop, NUM_VEHICLES, NUM_NODES, NUM_NODES)
    
    # -------------------------------------------------------------------------
    # A. PRIMARY OBJECTIVE: Total Travel Distance Minimization
    # -------------------------------------------------------------------------
    total_distance = np.sum(X * DISTANCE_MATRIX, axis=(1, 2, 3))  # shape: (num_pop,)
    
    # -------------------------------------------------------------------------
    # B. CONSTRAINT 1: Self-Loop Prohibition (x_{k, i, i} = 0)
    # -------------------------------------------------------------------------
    diag_indices = np.arange(NUM_NODES)
    self_loops = np.sum(X[:, :, diag_indices, diag_indices], axis=(1, 2))  # shape: (num_pop,)
    
    # -------------------------------------------------------------------------
    # C. CONSTRAINT 2: Customer Single Visit Constraint
    # Every customer j in {1..4} must have total entering arcs across all vehicles == 1
    # -------------------------------------------------------------------------
    customer_inflow = np.sum(X[:, :, :, 1:], axis=(1, 2))  # shape: (num_pop, 4)
    visit_violations = np.sum((customer_inflow - 1.0) ** 2, axis=1)  # shape: (num_pop,)
    
    # -------------------------------------------------------------------------
    # D. CONSTRAINT 3: Flow Conservation Constraint
    # For every vehicle k and node h: inflow == outflow
    # -------------------------------------------------------------------------
    inflow_per_node = np.sum(X, axis=2)   # shape: (num_pop, 2, 5)
    outflow_per_node = np.sum(X, axis=3)  # shape: (num_pop, 2, 5)
    flow_diff = inflow_per_node - outflow_per_node
    flow_violations = np.sum(flow_diff ** 2, axis=(1, 2))  # shape: (num_pop,)
    
    # -------------------------------------------------------------------------
    # E. CONSTRAINT 4: Vehicle Capacity Limits
    # Total demand of customers entered by vehicle k must <= VEHICLE_CAPACITY
    # -------------------------------------------------------------------------
    cust_demands = DEMANDS[1:].reshape(1, 1, 4)  # shape: (1, 1, 4)
    vehicle_inflow_cust = np.sum(X[:, :, :, 1:], axis=2)  # shape: (num_pop, 2, 4)
    vehicle_load = np.sum(vehicle_inflow_cust * cust_demands, axis=2)  # shape: (num_pop, 2)
    capacity_excess = np.maximum(vehicle_load - VEHICLE_CAPACITY, 0.0)
    capacity_violations = np.sum(capacity_excess, axis=1)  # shape: (num_pop,)
    
    # -------------------------------------------------------------------------
    # F. CONSTRAINT 5: Depot Return & Subtour Connectivity
    # If a vehicle visits customers, it MUST leave Depot 0 and return to Depot 0
    # -------------------------------------------------------------------------
    depot_outflow = np.sum(X[:, :, 0, 1:], axis=2)  # shape: (num_pop, 2)
    depot_inflow = np.sum(X[:, :, 1:, 0], axis=2)   # shape: (num_pop, 2)
    vehicle_active = (np.sum(X[:, :, :, 1:], axis=(2, 3)) > 0).astype(float)
    
    no_depot_start = np.maximum(vehicle_active - depot_outflow, 0.0)
    no_depot_return = np.maximum(vehicle_active - depot_inflow, 0.0)
    subtour_violations = np.sum(no_depot_start + no_depot_return, axis=1)
    
    # -------------------------------------------------------------------------
    # COMBINED FITNESS FUNCTION (MINIMIZATION)
    # -------------------------------------------------------------------------
    fitness = (total_distance +
               P_SELF_LOOP * self_loops +
               P_VISIT * visit_violations +
               P_FLOW * flow_violations +
               P_CAPACITY * capacity_violations +
               P_SUBTOUR * subtour_violations)
    
    return fitness


def print_cvrp_solution(best_vector):
    """Parses and renders the 3D CVRP routing matrix into human-readable tours."""
    X = np.round(best_vector).reshape(NUM_VEHICLES, NUM_NODES, NUM_NODES).astype(int)
    
    print("\n" + "=" * 65)
    print(" OPTIMAL CVRP VEHICLE ROUTING SCHEDULE ")
    print("=" * 65)
    
    total_tour_distance = 0.0
    all_visited = set()
    
    for k in range(NUM_VEHICLES):
        print(f"\n[Vehicle {k + 1}]")
        arcs = []
        for i in range(NUM_NODES):
            for j in range(NUM_NODES):
                if X[k, i, j] == 1:
                    arcs.append((i, j))
                    
        if not arcs:
            print("   (Vehicle unused)")
            continue
            
        current_node = 0
        tour = [0]
        v_load = 0
        v_dist = 0.0
        
        step = 0
        while step < NUM_NODES + 2:
            next_nodes = [j for (i, j) in arcs if i == current_node]
            if not next_nodes:
                break
            next_node = next_nodes[0]
            v_dist += DISTANCE_MATRIX[current_node, next_node]
            tour.append(next_node)
            if next_node != 0:
                v_load += DEMANDS[next_node]
                all_visited.add(next_node)
            current_node = next_node
            step += 1
            if current_node == 0 and len(tour) > 1:
                break
                
        tour_str = " -> ".join(map(str, tour))
        print(f"   Route: {tour_str}")
        print(f"   Distance: {v_dist:.2f} km")
        print(f"   Vehicle Load: {v_load} / {VEHICLE_CAPACITY:.0f} units")
        total_tour_distance += v_dist
        
    print("-" * 65)
    print(f"Visited Customers: {sorted(list(all_visited))} / {[1, 2, 3, 4]}")
    print(f"[SUMMARY] Total Fleet Distance: {total_tour_distance:.2f} km")
    print("=" * 65)


def main():
    print("=================================================================")
    print(" BQPhy Step 3: Pure Quantum-Inspired Miniature CVRP Optimizer   ")
    print("=================================================================")
    print(f"Depot: Node 0 | Customers: Nodes 1..4 | Vehicles: {NUM_VEHICLES}")
    print(f"Total Decision Variables: {NUM_VARIABLES} (2 x 5 x 5 matrix)")
    print(f"Vehicle Capacity: {VEHICLE_CAPACITY} units")
    print("-----------------------------------------------------------------")
    
    config = {
        "numPopulation": 200,           # 200 quantum state vectors
        "maxGeneration": 800,           # 800 evolution generations
        "deltaTheta": 0.12,             # Rotation gate step size 0.12 rad (~6.8 degrees)
        "designVariables": NUM_VARIABLES,# 50 binary decision variables
        "typeOfOptimisation": "BINARY",
        "populationInitialSeeding": False,
        "outputFilePath": "step3_cvrp_output",
        "generationLogging": "noLogging",
    }
    
    print("[1] Initializing BQPhy C++ Engine...")
    optimizer = qea.BQPhy_OPTIMISER()
    optimizer.initialize(config)
    
    print("[2] Registering CVRP Vectorized Tensor Fitness Function...")
    optimizer.model(evaluate_cvrp_fitness)
    
    print("[3] Launching Quantum-Inspired Evolutionary Optimization...")
    optimizer.runOptimization()
    
    print("[4] Solution Converged! Extracting Best Design...")
    best_vector, best_fitness = optimizer.getBestDesign()
    optimizer.writeCSV()
    
    print_cvrp_solution(best_vector)

if __name__ == "__main__":
    main()
