#!/usr/bin/env python3
"""
BQPhy Binary Optimization Example - Knapsack Problem
Demonstrates binary optimization using BQPhy for a 0-1 knapsack problem.

The knapsack problem: given a set of items with weights and values,
select items to maximize value while staying within weight capacity.
"""

import numpy as np
import bqphy.BQPhy_Optimiser as qea

# Problem data - small knapsack instance
ITEMS = [
    {"value": 60, "weight": 10},   # Item 0
    {"value": 100, "weight": 20},  # Item 1
    {"value": 120, "weight": 30},  # Item 2
    {"value": 80, "weight": 15},   # Item 3
    {"value": 90, "weight": 25},   # Item 4
    {"value": 150, "weight": 35},  # Item 5
    {"value": 70, "weight": 12},   # Item 6
    {"value": 110, "weight": 28},  # Item 7
]
CAPACITY = 50

def knapsack_fitness(x):
    """
    Knapsack fitness function (to be minimized)
    
    Args:
        x: Binary array where x.shape = (Total_population, number_of_items)
    
    Returns:
        Array of float: Negative value (since we minimize) with penalty for overweight
    """
    
    Weights = np.array([item["weight"] for item in ITEMS])
    Values = np.array([item["value"] for item in ITEMS])

    # print(f"Debug: x.shape = {x.shape}, Weights.shape = {Weights.shape}, Values.shape = {Values.shape}")

    # If x is a 1D vector of selection variables:
    total_weights = x @ Weights
    total_values = x @ Values


    # Fitness: negative value (since you’re minimizing) + penalty
    fitness = -total_values
    penalty = np.maximum(total_weights - CAPACITY, 0)
    penaltyCoeff = 1000
    fitness += penalty * penaltyCoeff  # Large penalty for exceeding capacity

    return fitness

def display_solution(solution):
    """Display the knapsack solution in a readable format"""
    selected_items = [i for i, selected in enumerate(solution) if selected == 1]
    total_weight = sum(ITEMS[i]["weight"] for i in selected_items)
    total_value = sum(ITEMS[i]["value"] for i in selected_items)
    
    print(f"📦 Selected Items:")
    for i in selected_items:
        print(f"   Item {i}: Value={ITEMS[i]['value']}, Weight={ITEMS[i]['weight']}")
    
    print(f"\n📊 Summary:")
    print(f"   Total Value: {total_value}")
    print(f"   Total Weight: {total_weight}/{CAPACITY}")
    print(f"   Capacity Used: {total_weight/CAPACITY*100:.1f}%")
    
    return total_value, total_weight

def main():
    print("🚀 BQPhy Binary Optimization Example")
    print("🎒 Problem: 0-1 Knapsack Optimization")
    print("=" * 60)
    
    # Display problem instance
    print("📋 Available Items:")
    for i, item in enumerate(ITEMS):
        ratio = item["value"] / item["weight"]
        print(f"   Item {i}: Value={item['value']:3d}, Weight={item['weight']:2d}, Ratio={ratio:.1f}")
    print(f"\n🎯 Knapsack Capacity: {CAPACITY}")
    print()
    
    # Problem configuration
    config = {
        "numPopulation": 20,
        "maxGeneration": 200,
        "deltaTheta": .05,
        "designVariables": len(ITEMS),
        "typeOfOptimisation":"BINARY",

        "populationInitialSeeding": True,                                       # True to enable user-defined initial population seeding
        "populationInitCSVFilePath": "../../python/examples/k8_popInit.csv",    # Path to CSV file for initial population seeding
        
        # Output configuration
        "outputFilePath": "optimization_results",       # Custom output directory
        "generationLogging": "noLogging",               # "noLogging" for no logging or "minimumLogging" to Enable less detailed logging or "verboseLogging" to Enable detailed logging
    }
    
    
    # Initialize optimizer
    print("🔄 Initializing BQPhy optimizer...")
    optimizer = qea.BQPhy_OPTIMISER()
    optimizer.initialize(config)
    
    optimizer.model(knapsack_fitness)
    
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
    print(f"🎯 Best Solution: {best_solution}")
    print(f"📈 Best Fitness: {best_fitness}")
    
    total_value, total_weight = display_solution(best_solution)
    
    # Check if solution is feasible
    feasible = total_weight <= CAPACITY
    print(f"\n🏆 Solution Status: {'✅ Feasible' if feasible else '❌ Infeasible'}")
    
    # Calculate efficiency
    if feasible:
        efficiency = total_value / CAPACITY  # value per unit capacity
        print(f"💡 Efficiency: {efficiency:.2f} value per unit capacity")

if __name__ == "__main__":
    main()