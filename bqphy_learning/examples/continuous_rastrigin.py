#!/usr/bin/env python3
"""
BQPhy Continuous Optimization Example - Rastrigin Function
Demonstrates optimization of a multi-modal continuous function using BQPhy.

The Rastrigin function is a highly multi-modal function with many local optima,
making it a challenging test case for optimization algorithms.
"""

import numpy as np
import bqphy.BQPhy_Optimiser as qea

def rastrigin_function(x):
    """
    Rastrigin function - a common optimization test function
    Global minimum: f(0,0,...,0) = 0
    
    Args:
        x: List or array of design variables for total population, shape (Total_population, designVariables)
    
    Returns:
        Array of float: Function value
    """
    A = 10
    fitness=np.zeros(x.shape[0],dtype=np.float64)
    for i in range(x.shape[0]):
        fitness[i]= (A * x.shape[1] + np.sum(x[i]**2 - A * np.cos(2 * np.pi * x[i])))
    return fitness

def main():
    print("🚀 BQPhy Continuous Optimization Example")
    print("📊 Problem: Rastrigin Function Minimization")
    print("=" * 60)
    
    # Problem configuration
    config = {
        "numPopulation": 200,
        "maxGeneration": 500,
        # "deltaTheta": .05,
        "designVariables": 4,
        "typeOfOptimisation":"CONTINUOUS",
        "lowerBounds": [-5.12] * 4,
        "upperBounds": [5.12] * 4,
        "encodingType": "real",  # "binary" or "real" encoding for design variables
        "lamda": 2.5,  # Balance between exploration and exploitation (0 to 1)

        # # Initial population seeding configuration
        # "populationInitialSeeding": True,                                         # True to enable user-defined initial population seeding
        # "populationInitCSVFilePath": "rast_popInit.csv",                          # Path to CSV file for initial population seeding (optional, only used if populationInitialSeeding is True)

        # Output configuration
        "outputFilePath": "optimization_results_rastrigin",         # Custom output directory
        "generationLogging": "verboseLogging",                           # "noLogging" for no logging or "minimumLogging" to Enable less detailed logging or "verboseLogging" to Enable detailed logging

        # Convergence criteria configuration
        # "convergenceCondition": "fitnessStagnation",    # "generationCount" or "fitnessStagnation" (default is "fitnessStagnation" with stagnationGenerations = 20)
        # "stagnationGenerations": 20,                    # Number of generations to check for fitness stagnation (only relevant if convergenceCondition is "fitnessStagnation")

        # # Restart configuration
        # "restartDump": True,
        # "restartDumpFrequency": 30,
        # "restartDumpPath": "Myrestart/restart_data.txt",

        # # To restart from a previous run, set "natureOfRun" to "restartSolver" and provide the path to the restart data files using "restartReadPath". 
        # # The path can include wildcards (e.g., "Myrestart/restart_data_*.txt") to read latest written files if needed.
        # "natureOfRun": "restartSolver",               # "newRun" for fresh run or "restartSolver" to restart from previous run
        # "restartReadPath": "Myrestart/restart_data_*.txt"
    }
    
    
    # Initialize optimizer
    print("🔄 Initializing BQPhy optimizer...")
    optimizer = qea.BQPhy_OPTIMISER()
    optimizer.initialize(config)
    optimizer.model(rastrigin_function)
    
    # Run optimization
    print("⚡ Running optimization...")
    optimizer.runOptimization()     # "cpu" can also be specified for serial execution # "openmp" for parallel execution # "gpu" for GPU execution

    # Get best solution
    best_solution, best_fitness = optimizer.getBestDesign()

    # This will create the folder with path: "outputFilePath" containing result CSV files
    optimizer.writeCSV()

    
    
    # Display results
    print("\n" + "=" * 60)
    print("✅ Optimization Complete!")
    print(f"🎯 Best Solution: {[f'{x:.6f}' for x in best_solution]}")
    print(f"📈 Best Fitness: {best_fitness[-1]:.8f}")
    print(f"🏆 Expected: All zeros with fitness ≈ 0.0")
    print(f"🎖️  Quality: {'Excellent' if best_fitness[-1] < 1e-3 else 'Good' if best_fitness[-1] < 1.0 else 'Fair'}")

if __name__ == "__main__":
    main()