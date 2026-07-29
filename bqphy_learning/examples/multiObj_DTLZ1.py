#!/usr/bin/env python3
"""
BQPhy Multi-Objective Optimization Example
Benchmark: ZDT3

ZDT3 Properties:
- 2 objectives
- Disconnected Pareto front
- Standard benchmark for multi-objective optimizers

True Pareto front:
f2 = 1 - sqrt(f1)
where f1 in [0,1]
"""

import numpy as np
import matplotlib.pyplot as plt
import bqphy.BQPhy_Optimiser as qea


# ------------------------------------------------------------
# ZDT3 Objective Function
# ------------------------------------------------------------
def dtlz1(x, numObjectives=3):
    """
    DTLZ1 benchmark problem

    Parameters
    ----------
    x : ndarray
        shape (population, dimensions)

    numObjectives : int
        number of objectives

    Returns
    -------
    fitness : ndarray
        shape (population, numObjectives)
    """

    numPop = x.shape[0]
    dim = x.shape[1]

    k = dim - numObjectives + 1

    fitness = np.zeros((numPop, numObjectives), dtype=np.float64)

    g = 100 * (
        k
        + np.sum(
            (x[:, -k:] - 0.5) ** 2
            - np.cos(20 * np.pi * (x[:, -k:] - 0.5)),
            axis=1
        )
    )

    for i in range(numPop):

        for m in range(numObjectives):

            f = 0.5 * (1 + g[i])

            for j in range(numObjectives - m - 1):
                f *= x[i, j]

            if m > 0:
                f *= (1 - x[i, numObjectives - m - 1])

            fitness[i, m] = f

    return fitness

# ------------------------------------------------------------
# Plot Pareto Front
# ------------------------------------------------------------
def plot_pareto(fitness, num_points=2000):
# def plot_dtlz1(fitness, num_points=2000):

    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    if fitness.shape[1] != 3:
        raise ValueError("DTLZ1 plot supports only 3 objectives")

    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection='3d')

    # --------------------------------------------------------
    # Obtained Pareto Front
    # --------------------------------------------------------
    ax.scatter(
        fitness[:, 0],
        fitness[:, 1],
        fitness[:, 2],
        label="Obtained Pareto Front"
    )

    # --------------------------------------------------------
    # TRUE Pareto Front
    # f1 + f2 + f3 = 0.5
    # --------------------------------------------------------

    true_pf = []

    while len(true_pf) < num_points:

        f1 = np.random.uniform(0, 0.5)
        f2 = np.random.uniform(0, 0.5)

        f3 = 0.5 - f1 - f2

        if f3 >= 0:
            true_pf.append([f1, f2, f3])

    true_pf = np.array(true_pf)

    ax.scatter(
        true_pf[:, 0],
        true_pf[:, 1],
        true_pf[:, 2],
        alpha=0.2,
        label="True Pareto Front"
    )

    plt.gca().invert_yaxis()

    ax.set_xlabel("f1")
    ax.set_ylabel("f2")
    ax.set_zlabel("f3")

    ax.set_title("DTLZ1 Pareto Front")

    plt.legend()
    plt.show()

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():

    print("🚀 BQPhy Multi-Objective Optimization")
    print("📊 Benchmark: DTLZ1")
    print("=" * 60)

    numObjectives = 3

    config = {
        "numPopulation": 500,
        "maxGeneration": 3000,
        "designVariables": numObjectives + 4,

        "typeOfOptimisation": "CONTINUOUS",

        "lowerBounds": [0.0] * (numObjectives + 4),
        "upperBounds": [1.0] * (numObjectives + 4),

        # Logging
        "outputFilePath": "dtlz1_results",
        "generationLogging": "noLogging",
    }

    # --------------------------------------------------------
    # Initialize optimizer
    # --------------------------------------------------------
    optimizer = qea.BQPhy_OPTIMISER()

    optimizer.initialize(config)

    optimizer.model(dtlz1)

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