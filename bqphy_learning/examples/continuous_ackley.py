#!/usr/bin/env python3
"""
BQPhy Continuous Optimization Example - Ackley Function
Demonstrates optimization of a multi-modal continuous function using BQPhy.

The Ackley function is a highly multi-modal function with many local optima,
making it a challenging test case for optimization algorithms.
"""

import numpy as np
import bqphy.BQPhy_Optimiser as qea

def ackley_function(x):
    """
    Ackley function - a common optimization test function
    Global minimum: f(0,0,...,0) = 0
    
    Args:
        x: List or array of design variables for total population,
           shape (Total_population, designVariables)
    
    Returns:
        Array of float: Function value
    """
    a = 20
    b = 0.2
    c = 2 * np.pi

    fitness = np.zeros(x.shape[0], dtype=np.float64)

    for i in range(x.shape[0]):
        n = x.shape[1]
        sum_sq = np.sum(x[i] ** 2)
        sum_cos = np.sum(np.cos(c * x[i]))

        term1 = -a * np.exp(-b * np.sqrt(sum_sq / n))
        term2 = -np.exp(sum_cos / n)

        fitness[i] = term1 + term2 + a + np.e

    return fitness

def main():
    print("🚀 BQPhy Continuous Optimization Example")
    print("📊 Problem: Ackley Function Minimization")
    print("=" * 60)
    
    # Problem configuration
    config = {
        "numPopulation": 100,
        "maxGeneration": 2000,
        "deltaTheta": .05,
        "designVariables": 5,
        
        "typeOfOptimisation":"MIXED",
        "lowerBounds": [-5.12] * 5,
        "upperBounds": [5.12] * 5,

        "variableTypes": ["int", "int", "int", "int", "float"],  # "float" for continuous variables, "int" for discrete variables (only relevant if typeOfOptimisation is "MIXED")
        "midowApproach": "bucket",                      # "round" or "bucket" options for handling mid-point values in mixed optimization (only relevant if typeOfOptimisation is "MIXED")

        # Output configuration
        "outputFilePath": "optimization_results_2",       # Custom output directory
        "generationLogging": "noLogging",               # "noLogging" for no logging or "minimumLogging" to Enable less detailed logging or "verboseLogging" to Enable detailed logging

        # Convergence criteria configuration
        "convergenceCondition": "fitnessStagnation",    # "generationCount" or "fitnessStagnation"
        "stagnationGenerations": 20,                    # Number of generations to check for fitness stagnation (only relevant if convergenceCondition is "fitnessStagnation")
    }
    
    
    # Initialize optimizer
    print("🔄 Initializing BQPhy optimizer...")
    optimizer = qea.BQPhy_OPTIMISER()
    optimizer.initialize(config)
    optimizer.model(ackley_function)
    
    # Run optimization
    print("⚡ Running optimization...")
    optimizer.runOptimization()     # "cpu" can also be specified for serial execution # "openmp" for parallel execution # "gpu" for GPU execution

    # Get best solution
    best_solution, best_fitness = optimizer.getBestDesign()

    # This will create the folder with "outputFilePath" path containing result CSV files 
    # or if "outputFilePath" is not specified default path: Run_YYYY-MM-DD-HH-MM-SS containing result CSV files
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