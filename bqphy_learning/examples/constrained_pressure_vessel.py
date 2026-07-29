#!/usr/bin/env python3
"""
BQPhy Constrained Optimization Example - Engineering Design
Demonstrates constrained optimization using BQPhy for a pressure vessel design problem.

This example shows how to handle multiple constraints in an engineering design context.
"""

import numpy as np
import bqphy.BQPhy_Optimiser as qea


def pressure_vessel_fitness(x):
    """
    Pressure vessel design optimization (vectorized for populations)

    Parameters
    ----------
    x : np.ndarray, shape (numPop, 4)
        Each row represents [Ts, Th, R, L]

    Returns
    -------
    fitness : np.ndarray, shape (numPop,)
        Penalized objective values (lower is better)
    """
    Ts, Th, R, L = x[:, 0], x[:, 1], x[:, 2], x[:, 3]

    # --- Objective ---
    material_cost = (
        0.6224 * Ts * R * L +
        1.7781 * Th * R**2 +
        3.1661 * Ts**2 * L +
        19.84  * Ts**2 * R
    )

    # --- Constraints ---
    g1 = -Ts + 0.0193 * R
    g2 = -Th + 0.00954 * R
    g3 = -np.pi * R**2 * L - (4/3)*np.pi*R**3 + 1296000
    g4 = L - 240

    # --- Penalties ---
    penalty = (
        np.where(g1 > 0, g1**2, 0) +
        np.where(g2 > 0, g2**2, 0) +
        np.where(g3 > 0, g3**2, 0) +
        np.where(g4 > 0, g4**2, 0) +
        np.where(Ts < 0.0625, (0.0625 - Ts)**2, 0) +
        np.where(Th < 0.0625, (0.0625 - Th)**2, 0)
    )

    ratio = L / R
    penalty += np.where(ratio > 20, (ratio - 20)**2, 0)
    penalty += np.where(ratio < 2,  (2 - ratio)**2, 0)

    # --- Combine objective and penalty ---
    fitness = material_cost + 1e5 * penalty

    return fitness



def display_design(solution):
    """Display the pressure vessel design in a readable format"""
    Ts, Th, R, L = solution
    
    print("🔧 Pressure Vessel Design:")
    print(f"   Shell Thickness (Ts): {Ts:.4f} inches")
    print(f"   Head Thickness (Th):  {Th:.4f} inches") 
    print(f"   Inner Radius (R):     {R:.2f} inches")
    print(f"   Length (L):           {L:.2f} inches")
    
    # Calculate derived properties
    volume = np.pi * R**2 * L + (4/3) * np.pi * R**3
    surface_area = 2 * np.pi * R * L + 4 * np.pi * R**2
    
    print(f"\n📊 Design Properties:")
    print(f"   Internal Volume:      {volume:.0f} cubic inches")
    print(f"   Surface Area:         {surface_area:.0f} square inches")
    print(f"   Length/Radius Ratio:  {L/R:.2f}")
    
    # Calculate cost components
    material_cost = 0.6224 * Ts * R * L + 1.7781 * Th * R**2 + 3.1661 * Ts**2 * L + 19.84 * Ts**2 * R
    
    print(f"\n💰 Cost Analysis:")
    print(f"   Total Material Cost:  ${material_cost:.2f}")
    
    # Check constraints
    print(f"\n✅ Constraint Check:")
    
    g1 = -Ts + 0.0193 * R
    print(f"   Shell thickness:      {'✅' if g1 <= 0 else '❌'} ({g1:.6f} ≤ 0)")
    
    g2 = -Th + 0.00954 * R  
    print(f"   Head thickness:       {'✅' if g2 <= 0 else '❌'} ({g2:.6f} ≤ 0)")
    
    g3 = -np.pi * R**2 * L - (4/3) * np.pi * R**3 + 1296000
    print(f"   Volume constraint:    {'✅' if g3 <= 0 else '❌'} ({g3:.0f} ≤ 0)")
    
    g4 = L - 240
    print(f"   Length constraint:    {'✅' if g4 <= 0 else '❌'} ({g4:.2f} ≤ 0)")
    
    # Engineering feasibility
    feasible = all([g1 <= 0, g2 <= 0, g3 <= 0, g4 <= 0, 
                   Ts >= 0.0625, Th >= 0.0625, 2 <= L/R <= 20])
    
    print(f"\n🏆 Design Status: {'✅ Feasible' if feasible else '❌ Infeasible'}")

def main():
    print("🚀 BQPhy Constrained Optimization Example")
    print("⚙️  Problem: Pressure Vessel Design Optimization")
    print("=" * 60)
    
    print("🎯 Objective: Minimize material cost")
    print("📋 Design Variables:")
    print("   - Shell thickness (Ts)")
    print("   - Head thickness (Th)")
    print("   - Inner radius (R)")
    print("   - Cylindrical length (L)")
    
    print("\n📐 Constraints:")
    print("   - Stress constraints on shell and head")
    print("   - Minimum volume requirement")
    print("   - Maximum length limitation")
    print("   - Minimum thickness requirements")
    print("   - Reasonable design ratios")
    print()
    
    # Problem configuration
    config = {
        "numPopulation": 1000,
        "maxGeneration": 500,
        "deltaTheta": .05,
        "designVariables": 4,
        "typeOfOptimisation":"CONTINUOUS",

        # Output configuration
        "outputFilePath": "optimization_results",       # Custom output directory
        "generationLogging": "noLogging",               # "noLogging" for no logging or "minimumLogging" to Enable less detailed logging or "verboseLogging" to Enable detailed logging
    }
    lb=[0.0625, 0.0625, 10.0, 10.0]     # [Ts_min, Th_min, R_min, L_min]
    ub=[99.0, 99.0, 200.0, 240.0]         # [Ts_max, Th_max, R_max, L_max]
    config["lowerBounds"]=lb
    config["upperBounds"]=ub
    
    
    # Initialize optimizer
    print("🔄 Initializing BQPhy optimizer...")
    optimizer = qea.BQPhy_OPTIMISER()
    optimizer.initialize(config)
    optimizer.model(pressure_vessel_fitness)
    
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
    print(f"📈 Best Fitness (Cost): ${best_fitness[-1]:.2f}")
    
    display_design(best_solution)
    
    # Compare with typical values
    print(f"\n📚 Reference: Typical industrial pressure vessels")
    print(f"   Cost range: $5,000 - $15,000")
    print(f"   Performance: {'Excellent' if best_fitness[-1] < 8000 else 'Good' if best_fitness[-1] < 12000 else 'Fair'}")

if __name__ == "__main__":
    main()