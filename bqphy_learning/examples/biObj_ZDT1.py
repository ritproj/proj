#!/usr/bin/env python3
"""
BQPhy Multi-Objective Optimization Example
Benchmark: ZDT1

ZDT1 Properties:
- 2 objectives
- Convex Pareto front
- Standard benchmark for multi-objective optimizers

True Pareto front:
f2 = 1 - sqrt(f1)
where f1 in [0,1]
"""

import numpy as np
import matplotlib.pyplot as plt
import bqphy.BQPhy_Optimiser as qea


# ------------------------------------------------------------
# ZDT1 Objective Function
# ------------------------------------------------------------
def zdt1(x):
    """
    ZDT1 multi-objective benchmark

    Parameters
    ----------
    x : ndarray
        Shape: (population, designVariables)

    Returns
    -------
    fitness : ndarray
        Shape: (population, 2)
    """

    numPop = x.shape[0]
    dim = x.shape[1]

    fitness = np.zeros((numPop, 2), dtype=np.float64)

    # Objective 1
    f1 = x[:, 0]

    # g(x)
    g = 1.0 + 9.0 * np.sum(x[:, 1:], axis=1) / (dim - 1)

    # h(f1, g)
    h = 1.0 - np.sqrt(f1 / g)

    # Objective 2
    f2 = g * h

    fitness[:, 0] = f1
    fitness[:, 1] = f2

    return fitness


# ------------------------------------------------------------
# Plot Pareto Front
# ------------------------------------------------------------
def plot_pareto(fitness):
    """
    Plot obtained Pareto front
    """

    plt.figure(figsize=(7, 5))

    plt.scatter(
        fitness[:, 0],
        fitness[:, 1],
        label="Obtained Pareto Front"
    )

    # True Pareto Front
    x = np.linspace(0, 1, 200)
    y = 1 - np.sqrt(x)

    plt.plot(x, y, linewidth=2, label="True Pareto Front")

    plt.xlabel("Objective 1")
    plt.ylabel("Objective 2")
    plt.title("ZDT1 Pareto Front")
    plt.legend()
    plt.grid(True)

    plt.show()


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():

    print("🚀 BQPhy Multi-Objective Optimization")
    print("📊 Benchmark: ZDT1")
    print("=" * 60)

    dim = 30

    config = {

        # Optimizer
        "numPopulation": 100,
        "maxGeneration": 1000,
        "deltaTheta": 0.05,

        # Problem
        "designVariables": dim,
        "typeOfOptimisation": "CONTINUOUS",

        # Bounds
        "lowerBounds": [0.0] * dim,
        "upperBounds": [1.0] * dim,

        # Logging
        "outputFilePath": "zdt1_results",
        "generationLogging": "noLogging",
    }

    # --------------------------------------------------------
    # Initialize optimizer
    # --------------------------------------------------------
    optimizer = qea.BQPhy_OPTIMISER()

    optimizer.initialize(config)

    optimizer.model(zdt1)

    # --------------------------------------------------------
    # Run optimization
    # --------------------------------------------------------
    print("⚡ Running optimization...")
    optimizer.runOptimization()

    # --------------------------------------------------------
    # Get Pareto front
    # --------------------------------------------------------
    paretoSolutions, paretoFitness = optimizer.getParetoFront()

    paretoSolutions = np.array(paretoSolutions)
    paretoFitness = np.array(paretoFitness)

    print("\n✅ Optimization Complete")
    print(f"Pareto solutions: {paretoSolutions.shape[0]}")
    print(f"Objectives: {paretoFitness.shape[1]}")
    print("Multi-objective Fitness:", paretoFitness)
    # --------------------------------------------------------
    # Plot results
    # --------------------------------------------------------
    plot_pareto(paretoFitness)

    # # --------------------------------------------------------
    # # Save CSV
    # # --------------------------------------------------------
    # optimizer.writeCSV()


if __name__ == "__main__":
    main()