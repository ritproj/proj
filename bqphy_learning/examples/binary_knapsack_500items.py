#!/usr/bin/env python3
"""
BQPhy Binary Optimization Example - Knapsack Problem
Demonstrates binary optimization using BQPhy for a 0-1 knapsack problem.

The knapsack problem: given a set of items with weights and values,
select items to maximize value while staying within weight capacity.
"""

import numpy as np
import bqphy.BQPhy_Optimiser as qea

# Problem data - large knapsack instance
Values = np.array([
    47, 107, 53, 139, 179, 106, 92, 93, 35, 48, 40, 175,
    111, 60, 158, 78, 179, 20, 3, 188, 82, 140, 7, 194, 35, 181, 157, 36, 35, 193,
    63, 200, 160, 100, 101, 94, 185, 144, 72, 112, 72, 71, 24, 49, 147, 31, 175, 156,
    67, 155, 128, 114, 122, 156, 94, 193, 120, 141, 177, 134, 195, 11, 49, 65, 54, 46,
    185, 180, 123, 174, 117, 147, 150, 23, 75, 192, 35, 80, 84, 78, 18, 98, 119, 141,
    89, 90, 98, 99, 119, 61, 200, 24, 157, 196, 199, 14, 48, 193, 124, 168, 112, 164,
    132, 126, 117, 193, 93, 1, 70, 112, 48, 71, 193, 181, 100, 150, 88, 81, 24, 30, 49,
    178, 28, 142, 119, 162, 137, 38, 30, 67, 150, 155, 81, 21, 31, 63, 58, 141, 84, 36,
    125, 21, 187, 68, 184, 49, 162, 190, 12, 116, 68, 180, 76, 75, 41, 21, 97, 154, 112,
    93, 176, 94, 157, 76, 200, 59, 191, 141, 55, 37, 162, 172, 87, 130, 12, 81, 86, 170,
    66, 66, 109, 55, 186, 96, 160, 116, 198, 38, 8, 147, 88, 68, 85, 193, 92, 27, 47, 
    135, 56, 61, 18, 52, 71, 2, 122, 44, 53, 100, 133, 13, 59, 146, 133, 153, 32, 190, 
    157, 183, 110, 38, 134, 181, 26, 62, 197, 184, 48, 49, 57, 195, 81, 161, 63, 10, 
    146, 29, 13, 186, 87, 9, 197, 111, 29, 166, 130, 21, 41, 144, 132, 167, 148, 191, 
    174, 42, 83, 176, 77, 20, 128, 74, 83, 48, 119, 45, 148, 87, 183, 127, 129, 21, 
    125, 104, 76, 122, 120, 102, 79, 54, 91, 64, 31, 191, 156, 195, 74, 52, 147, 16, 
    90, 34, 77, 54, 109, 146, 154, 102, 114, 21, 98, 93, 186, 112, 31, 51, 127, 57, 
    53, 118, 102, 165, 82, 138, 141, 127, 185, 186, 4, 190, 175, 168, 118, 80, 181, 
    187, 46, 164, 8, 141, 171, 149, 116, 162, 69, 156, 63, 63, 124, 51, 28, 113, 106, 
    29, 76, 147, 55, 21, 94, 101, 197, 158, 19, 158, 38, 37, 174, 178, 105, 140, 23, 
    33, 67, 167, 51, 174, 197, 191, 93, 160, 107, 148, 167, 37, 25, 52, 67, 97, 97, 
    1, 144, 51, 149, 72, 12, 19, 28, 61, 56, 172, 157, 115, 39, 43, 31, 13, 114, 199, 
    189, 129, 115, 65, 181, 188, 138, 29, 52, 82, 163, 77, 105, 147, 110, 46, 198, 109,
    41, 187, 139, 151, 73, 94, 8, 22, 57, 109, 29, 103, 30, 116, 16, 190, 184, 155, 96,
    92, 126, 137, 183, 127, 4, 11, 169, 161, 89, 144, 138, 51, 80, 65, 156, 150, 132, 
    122, 61, 23, 198, 3, 168, 120, 184, 159, 10, 52, 22, 163, 28, 189, 192, 130, 182, 
    96, 34, 56, 174, 162, 175, 199, 146, 82, 35, 152, 115, 20, 74, 10, 94, 189, 94, 
    16, 68, 156, 175, 185, 108, 17, 94, 21, 29, 34, 92, 34
], dtype=np.int32)

Weights = np.array([
    29, 76, 30, 86, 132, 83, 98, 175, 98, 141, 179, 74,
    24, 96, 87, 146, 43, 199, 177, 107, 60, 182, 41, 171, 31, 151, 181, 92, 197, 152,
    59, 43, 41, 109, 197, 41, 104, 48, 45, 22, 39, 89, 181, 189, 77, 19, 6, 159, 42,
    112, 40, 90, 161, 7, 40, 172, 128, 84, 90, 156, 35, 6, 76, 115, 127, 33, 86, 67,
    42, 19, 67, 191, 68, 8, 39, 75, 113, 180, 173, 132, 44, 197, 162, 159, 4, 88, 124,
    29, 159, 71, 151, 143, 167, 175, 76, 27, 121, 160, 181, 7, 37, 154, 73, 190, 112,
    95, 82, 40, 200, 92, 65, 129, 188, 185, 176, 13, 35, 29, 15, 23, 65, 78, 172, 6,
    24, 125, 193, 106, 34, 168, 93, 4, 15, 96, 9, 134, 42, 130, 17, 10, 49, 111, 44,
    21, 23, 34, 77, 124, 129, 56, 124, 129, 168, 185, 86, 43, 82, 104, 105, 135, 177,
    67, 86, 197, 140, 19, 8, 177, 32, 193, 19, 129, 50, 132, 190, 78, 27, 193, 59, 
    58, 151, 72, 185, 8, 152, 11, 180, 179, 144, 197, 4, 183, 172, 149, 120, 40, 59,
    1, 50, 109, 78, 142, 68, 38, 61, 154, 102, 190, 173, 73, 31, 88, 23, 145, 80, 130,
    54, 11, 184, 180, 121, 17, 31, 77, 134, 190, 143, 51, 69, 117, 80, 123, 108, 189,
    82, 189, 174, 46, 71, 192, 127, 35, 138, 143, 172, 147, 118, 177, 47, 40, 144, 87,
    29, 189, 128, 142, 50, 191, 184, 175, 192, 167, 102, 71, 118, 168, 111, 179, 47,
    196, 123, 161, 132, 109, 17, 104, 13, 105, 177, 31, 154, 136, 114, 46, 14, 120,
    137, 55, 81, 24, 91, 18, 111, 85, 118, 107, 128, 162, 66, 90, 66, 143, 116, 35,
    191, 160, 187, 59, 62, 54, 52, 143, 30, 156, 161, 21, 133, 16, 198, 161, 155, 
    174, 142, 29, 26, 103, 30, 22, 112, 162, 119, 171, 112, 118, 194, 45, 36, 103,
    134, 104, 184, 183, 169, 171, 90, 101, 103, 11, 135, 60, 21, 184, 139, 123, 129,
    152, 141, 193, 159, 143, 197, 43, 143, 117, 95, 43, 17, 31, 26, 135, 129, 36, 
    188, 184, 22, 175, 67, 64, 190, 34, 132, 152, 50, 159, 147, 121, 96, 120, 8, 94,
    52, 161, 96, 198, 107, 59, 13, 69, 173, 182, 56, 178, 155, 159, 32, 50, 86, 80,
    3, 6, 91, 120, 93, 123, 186, 40, 29, 35, 136, 174, 56, 46, 62, 1, 140, 81, 174,
    67, 43, 166, 168, 45, 131, 128, 166, 78, 29, 136, 87, 136, 148, 20, 113, 79, 71,
    119, 100, 8, 55, 59, 75, 33, 139, 190, 109, 60, 122, 74, 119, 174, 140, 199, 68,
    92, 137, 43, 61, 173, 125, 161, 93, 124, 45, 36, 76, 171, 26, 199, 6, 59, 95, 24,
    69, 18, 96, 26, 94, 47, 85, 191, 17, 194, 20, 164, 11, 112, 22, 116, 143, 141
], dtype=np.int32)

# Knapsack capacity
CAPACITY = 25233

def knapsack_fitness(x):
    """
    Knapsack fitness function (to be minimized)
    
    Args:
        x: Binary array where x.shape = (Total_population, number_of_items)
    
    Returns:
        Array of float: Negative value (since we minimize) with penalty for overweight
    """
    
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
    total_weight = sum(Weights[i] for i in selected_items)
    total_value = sum(Values[i] for i in selected_items)
    
    print(f"📦 Selected Items:")
    for i in selected_items:
        print(f"   Item {i}: Value={Values[i]}, Weight={Weights[i]}")
    
    print(f"\n📊 Summary:")
    print(f"   Total Value: {total_value}")
    print(f"   Total Weight: {total_weight}/{CAPACITY}")
    print(f"   Capacity Used: {total_weight/CAPACITY*100:.1f}%")
    
    return total_value, total_weight

def main():
    print("🚀 BQPhy Binary Optimization Example")
    print("🎒 Problem: 0-1 Knapsack Optimization")
    print("=" * 60)
    
    print("📋 Available Items:")
    for i, (v, w) in enumerate(zip(Values, Weights)):
        ratio = v / w
        print(f"   Item {i}: Value={v:3d}, Weight={w:3d}, Ratio={ratio:.1f}")

    print(f"\n🎯 Knapsack Capacity: {CAPACITY}")
    print()


    
    # Problem configuration
    config = {
        "numPopulation": 100,
        "maxGeneration": 200,
        "deltaTheta": .05,
        "designVariables": len(Values),  # Number of items
        "typeOfOptimisation":"BINARY",

        # Output configuration
        "outputFilePath": "optimization_results",       # Custom output directory
        "generationLogging": "noLogging",               # "noLogging" for no logging or "minimumLogging" to Enable less detailed logging or "verboseLogging" to Enable detailed logging
    }
    
    
    # Initialize optimizer
    print("🔄 Initializing BQPhy optimizer")
    optimizer = qea.BQPhy_OPTIMISER()
    optimizer.initialize(config)
    optimizer.model(knapsack_fitness)
    
    # Run optimization
    print("⚡ Running optimization")
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