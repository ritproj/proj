#!/usr/bin/env python3
"""
Step 2: Standalone Task-to-Worker Binary Assignment Problem
Demonstrates BQPhy Optimizer Lifecycle, Vectorized Objective Matrix Math,
and Dual Penalty Handling (Equality Assignment & Inequality Workload Capacity).
"""

import sys
import numpy as np
import bqphy.BQPhy_Optimiser as qea

# Problem Definition Data
# 4 Tasks, 2 Workers
# Decision Variables: 4 tasks * 2 workers = 8 binary decision variables
NUM_TASKS = 4
NUM_WORKERS = 2
NUM_VARIABLES = NUM_TASKS * NUM_WORKERS

# Task duration / workload required
TASK_DURATIONS = np.array([10, 15, 20, 25])  # shape: (4,)

# Cost matrix C[task, worker]
# Row: Task (0..3), Column: Worker (0..1)
COST_MATRIX = np.array([
    [50, 80],   # Task 0 cost on Worker 0 vs Worker 1
    [40, 30],   # Task 1 cost on Worker 0 vs Worker 1
    [70, 40],   # Task 2 cost on Worker 0 vs Worker 1
    [60, 90],   # Task 3 cost on Worker 0 vs Worker 1
])  # shape: (4, 2)

# Worker capacity limits (Max total duration per worker)
WORKER_CAPACITIES = np.array([45, 45])  # shape: (2,)

# Penalty Scaling Factors
P_EQUALITY = 500.0    # Penalty scaling for violating single worker assignment rule
P_INEQUALITY = 200.0  # Penalty scaling for exceeding worker workload capacity


def evaluate_assignment_fitness(x_batch):
    """
    Vectorized Fitness Evaluation Callback for BQPhy.
    
    Args:
        x_batch (np.ndarray): 2D binary matrix of shape (numPopulation, NUM_VARIABLES)
                             where each row is a flattened decision vector of length 8.
                             Decision mapping: index k = task * NUM_WORKERS + worker.
                             
    Returns:
        np.ndarray: 1D fitness array of shape (numPopulation,) to be MINIMIZED.
    """
    num_pop = x_batch.shape[0]
    
    # Step 1: Reshape flattened decision vector (num_pop, 8) into 3D tensor (num_pop, 4, 2)
    # Tensor axes: (Candidate_i, Task_t, Worker_w)
    X = x_batch.reshape(num_pop, NUM_TASKS, NUM_WORKERS)
    
    # Step 2: Compute Primary Objective - Total Cost
    # Multiply selection tensor X(num_pop, 4, 2) by COST_MATRIX(4, 2) and sum over tasks & workers
    # Resulting shape: (num_pop,)
    total_cost = np.sum(X * COST_MATRIX, axis=(1, 2))
    
    # Step 3: Compute Equality Constraint Penalty - Task Single Assignment
    # Sum across workers (axis 2) for each task: sum_w X_{i, t, w}. Must equal 1 for all tasks.
    # Violation metric: squared deviation from 1.
    # Resulting sum across tasks shape: (num_pop,)
    assigned_workers_per_task = np.sum(X, axis=2)  # shape: (num_pop, 4)
    equality_violations = np.sum((assigned_workers_per_task - 1.0) ** 2, axis=1)  # shape: (num_pop,)
    
    # Step 4: Compute Inequality Constraint Penalty - Worker Capacity Limits
    # Calculate workload per worker: multiply X(num_pop, 4, 2) by TASK_DURATIONS(4, 1) and sum over tasks
    # Shape of worker_workloads: (num_pop, 2)
    task_durations_col = TASK_DURATIONS.reshape(NUM_TASKS, 1)
    worker_workloads = np.sum(X * task_durations_col, axis=1)  # shape: (num_pop, 2)
    
    # Excess workload above WORKER_CAPACITIES (45, 45)
    workload_excess = np.maximum(worker_workloads - WORKER_CAPACITIES, 0.0)  # shape: (num_pop, 2)
    inequality_violations = np.sum(workload_excess, axis=1)  # shape: (num_pop,)
    
    # Step 5: Total Combined Minimization Fitness
    fitness = (total_cost + 
               P_EQUALITY * equality_violations + 
               P_INEQUALITY * inequality_violations)
    
    return fitness


def main():
    print("=================================================================")
    print(" BQPhy Step 2: Standalone Task-Worker Binary Assignment Problem ")
    print("=================================================================")
    print(f"Tasks: {NUM_TASKS}, Workers: {NUM_WORKERS}")
    print(f"Total Binary Decision Variables: {NUM_VARIABLES}")
    print(f"Worker Capacity Limits: {WORKER_CAPACITIES}")
    print("-----------------------------------------------------------------")
    
    # BQPhy Configuration Dictionary
    config = {
        "numPopulation": 30,             # Number of quantum state vectors in population
        "maxGeneration": 150,            # Max iterations for quantum gate rotation loops
        "deltaTheta": 0.05,              # Quantum rotation gate angle (radians)
        "designVariables": NUM_VARIABLES,# 8 binary decision variables
        "typeOfOptimisation": "BINARY",  # Discrete 0/1 binary domain
        "populationInitialSeeding": False,# Uniform quantum superposition init (|alpha|^2 = |beta|^2 = 0.5)
        "outputFilePath": "step2_assignment_output", # Results folder
        "generationLogging": "noLogging",# Keep stdout clean
    }
    
    # BQPhy Optimizer Lifecycle
    print("[1] Instantiating C++ BQPhy_OPTIMISER object...")
    optimizer = qea.BQPhy_OPTIMISER()
    
    print("[2] Initializing optimizer configuration...")
    optimizer.initialize(config)
    
    print("[3] Binding vectorized fitness evaluation function...")
    optimizer.model(evaluate_assignment_fitness)
    
    print("[4] Executing quantum-inspired evolutionary optimization...")
    optimizer.runOptimization()
    
    print("[5] Extracting optimal solution vector...")
    best_vector, best_fitness_score = optimizer.getBestDesign()
    
    # Persist output files
    optimizer.writeCSV()
    
    # Post-Process & Interpret Results
    print("\n-----------------------------------------------------------------")
    print(" OPTIMIZATION RESULTS SUMMARY ")
    print("-----------------------------------------------------------------")
    print(f"Raw Decision Vector: {best_vector}")
    print(f"Best Combined Fitness Score: {best_fitness_score[0]:.2f}")
    
    # Reshape binary decision vector back to (4 tasks, 2 workers)
    assignment_matrix = np.round(best_vector).reshape(NUM_TASKS, NUM_WORKERS).astype(int)
    
    print("\nTask Assignment Matrix (Rows = Tasks 0..3, Cols = Workers 0..1):")
    print(assignment_matrix)
    
    # Verify assignment validity
    total_assigned_cost = 0
    print("\nDetailed Schedule:")
    for task in range(NUM_TASKS):
        assigned_worker = np.where(assignment_matrix[task] == 1)[0]
        if len(assigned_worker) == 1:
            w = assigned_worker[0]
            c = COST_MATRIX[task, w]
            d = TASK_DURATIONS[task]
            total_assigned_cost += c
            print(f"  - Task {task} (Duration: {d}m) -> Worker {w} (Cost: ${c})")
        else:
            print(f"  - Task {task} INVALID ASSIGNMENT: Assigned to {len(assigned_worker)} workers!")
            
    print("\nWorker Workload Check:")
    for w in range(NUM_WORKERS):
        tasks_for_w = np.where(assignment_matrix[:, w] == 1)[0]
        w_load = sum(TASK_DURATIONS[t] for t in tasks_for_w)
        status = "OK" if w_load <= WORKER_CAPACITIES[w] else "OVERLOADED"
        print(f"  - Worker {w}: Total Workload = {w_load}m / {WORKER_CAPACITIES[w]}m max [{status}]")
        
    print(f"\nFinal Valid Assignment Cost: ${total_assigned_cost}")
    print("=================================================================")

if __name__ == "__main__":
    main()
