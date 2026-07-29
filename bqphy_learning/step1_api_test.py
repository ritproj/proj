#!/usr/bin/env python3
"""
Step 1 API Test for BQPhy SDK
Runs the 8-item binary knapsack example to verify SDK setup and API binding functionality.
"""

import sys
import numpy as np
import bqphy.BQPhy_Optimiser as qea

def main():
    print("=== BQPhy SDK API Sanity Test ===")
    print(f"BQPhy Module: {qea}")
    
    # Simple test data
    items = [
        {"value": 60, "weight": 10},
        {"value": 100, "weight": 20},
        {"value": 120, "weight": 30},
        {"value": 80, "weight": 15},
        {"value": 90, "weight": 25},
        {"value": 150, "weight": 35},
        {"value": 70, "weight": 12},
        {"value": 110, "weight": 28},
    ]
    capacity = 50

    weights = np.array([item["weight"] for item in items])
    values = np.array([item["value"] for item in items])

    def fitness_fn(x):
        total_w = x @ weights
        total_v = x @ values
        fit = -total_v
        pen = np.maximum(total_w - capacity, 0)
        return fit + pen * 1000.0

    config = {
        "numPopulation": 20,
        "maxGeneration": 100,
        "deltaTheta": 0.05,
        "designVariables": len(items),
        "typeOfOptimisation": "BINARY",
        "populationInitialSeeding": False,
        "outputFilePath": "step1_test_output",
        "generationLogging": "noLogging",
    }

    optimizer = qea.BQPhy_OPTIMISER()
    optimizer.initialize(config)
    optimizer.model(fitness_fn)
    optimizer.runOptimization()

    best_sol, best_fit = optimizer.getBestDesign()
    print("[SUCCESS] BQPhy API Test Successful!")
    print(f"Best binary decision vector: {best_sol}")
    print(f"Best fitness score: {best_fit}")

if __name__ == "__main__":
    main()
