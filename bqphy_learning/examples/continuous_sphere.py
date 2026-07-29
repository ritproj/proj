#!/usr/bin/env python3
"""
BQPhy Continuous Optimization Example - Sphere Function
Demonstrates optimization of a simple continuous function using BQPhy.

The Sphere function is a simple unimodal function often used as a baseline
for testing optimization algorithms.
"""

import numpy as np
import bqphy.BQPhy_Optimiser as qea

def sphere_function(x):
    """
    Vectorized Sphere function for population-based optimization.
    
    Args:
        x : np.ndarray of shape (numPop, n_vars)
    
    Returns:
        np.ndarray of shape (numPop,)
        Each element is the fitness (sum of squares) for one individual.
    """
    return np.sum(x**2, axis=1)

def main():
    print("🚀 BQPhy Continuous Optimization Example")
    print("🌐 Problem: Sphere Function Minimization")
    print("=" * 60)
    
    # Problem configuration
    config = {
        "numPopulation": 100,
        "maxGeneration": 200,
        "deltaTheta": .05,
        "designVariables": 10,
        "typeOfOptimisation":"CONTINUOUS",
        "lowerBounds": [-10.0] * 10,
        "upperBounds": [10.0] * 10,

        # Output configuration
        "outputFilePath": "optimization_results",       # Custom output directory
        "generationLogging": "noLogging",               # "noLogging" for no logging or "minimumLogging" to Enable less detailed logging or "verboseLogging" to Enable detailed logging
    }
    
    
    # Initialize optimizer
    print("🔄 Initializing BQPhy optimizer...")
    optimizer = qea.BQPhy_OPTIMISER()
    optimizer.initialize(config)
    optimizer.model(sphere_function)
    
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
    print(f"🎯 Best Solution: {[f'{x:.6f}' for x in best_solution[:5]]}...")  # Show first 5
    print(f"📈 Best Fitness: {best_fitness[-1]:.10f}")
    print(f"🏆 Expected: All zeros with fitness = 0.0")
    
    # Calculate solution quality
    max_abs_value = max(abs(x) for x in best_solution)
    print(f"📊 Max absolute value: {max_abs_value:.6f}")
    
    if best_fitness[-1] < 1e-6:
        print("🎖️  Quality: Excellent convergence!")
    elif best_fitness[-1] < 1e-3:
        print("🎖️  Quality: Good convergence")
    else:
        print("🎖️  Quality: Fair convergence")

if __name__ == "__main__":
    main()