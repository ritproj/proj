import numpy as np

# Penalty Scaling Factors for BQPhy
P_VISIT = 15000.0     # High barrier penalty for unvisited/multi-visited customer
P_FLOW = 15000.0      # Penalty for flow conservation (inflow != outflow)
P_CAPACITY = 8000.0   # Penalty for exceeding vehicle capacity
P_SUBTOUR = 15000.0   # Penalty for isolated cycles disconnected from depot
P_SELF_LOOP = 30000.0 # Penalty for self-loops (i -> i)

def evaluate_qubo_energy(x: np.ndarray, Q_matrix: np.ndarray) -> float:
    """
    Evaluates the energy of a binary vector `x` given a QUBO matrix `Q_matrix`.
    Used primarily by the QAOA/Simulated Annealing solvers.
    """
    return float(x @ Q_matrix @ x)

def evaluate_cvrp_fitness(
    x_batch: np.ndarray, 
    distance_matrix: np.ndarray, 
    demands: np.ndarray, 
    vehicle_capacity: float, 
    num_vehicles: int, 
    num_nodes: int
) -> np.ndarray:
    """
    Vectorized CVRP Fitness Evaluation Callback used by BQPhy solver.
    
    Args:
        x_batch (np.ndarray): 2D matrix of shape (numPopulation, num_vars)
                              where num_vars = num_vehicles * num_nodes * num_nodes.
        distance_matrix (np.ndarray): shape (num_nodes, num_nodes)
        demands (np.ndarray): shape (num_nodes,), where demands[0] is typically 0 (depot)
        vehicle_capacity (float): Maximum capacity per vehicle.
        num_vehicles (int): Number of available vehicles.
        num_nodes (int): Total number of nodes (1 depot + customers).
                             
    Returns:
        np.ndarray: 1D fitness array of shape (numPopulation,) to be MINIMIZED.
    """
    num_pop = x_batch.shape[0]
    
    # Reshape (num_pop, num_vars) into 4D tensor X: (Candidate_pop, Vehicle_k, From_i, To_j)
    X = x_batch.reshape(num_pop, num_vehicles, num_nodes, num_nodes)
    
    # -------------------------------------------------------------------------
    # A. PRIMARY OBJECTIVE: Total Travel Distance Minimization
    # -------------------------------------------------------------------------
    total_distance = np.sum(X * distance_matrix, axis=(1, 2, 3))
    
    # -------------------------------------------------------------------------
    # B. CONSTRAINT 1: Self-Loop Prohibition (x_{k, i, i} = 0)
    # -------------------------------------------------------------------------
    diag_indices = np.arange(num_nodes)
    self_loops = np.sum(X[:, :, diag_indices, diag_indices], axis=(1, 2))
    
    # -------------------------------------------------------------------------
    # C. CONSTRAINT 2: Customer Single Visit Constraint
    # Every customer j in {1..N} must have total entering arcs across all vehicles == 1
    # -------------------------------------------------------------------------
    customer_inflow = np.sum(X[:, :, :, 1:], axis=(1, 2))
    visit_violations = np.sum((customer_inflow - 1.0) ** 2, axis=1)
    
    # -------------------------------------------------------------------------
    # D. CONSTRAINT 3: Flow Conservation Constraint
    # For every vehicle k and node h: inflow == outflow
    # -------------------------------------------------------------------------
    inflow_per_node = np.sum(X, axis=2)
    outflow_per_node = np.sum(X, axis=3)
    flow_diff = inflow_per_node - outflow_per_node
    flow_violations = np.sum(flow_diff ** 2, axis=(1, 2))
    
    # -------------------------------------------------------------------------
    # E. CONSTRAINT 4: Vehicle Capacity Limits
    # Total demand of customers entered by vehicle k must <= VEHICLE_CAPACITY
    # -------------------------------------------------------------------------
    cust_demands = demands[1:].reshape(1, 1, num_nodes - 1)
    vehicle_inflow_cust = np.sum(X[:, :, :, 1:], axis=2)
    vehicle_load = np.sum(vehicle_inflow_cust * cust_demands, axis=2)
    capacity_excess = np.maximum(vehicle_load - vehicle_capacity, 0.0)
    capacity_violations = np.sum(capacity_excess, axis=1)
    
    # -------------------------------------------------------------------------
    # F. CONSTRAINT 5: Depot Return & Subtour Connectivity
    # If a vehicle visits customers, it MUST leave Depot 0 and return to Depot 0
    # -------------------------------------------------------------------------
    depot_outflow = np.sum(X[:, :, 0, 1:], axis=2)
    depot_inflow = np.sum(X[:, :, 1:, 0], axis=2)
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
