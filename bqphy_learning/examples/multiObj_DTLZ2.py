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
# DTLZ2 Objective Function
# ------------------------------------------------------------
def dtlz2(x, numObjectives=3):
    """
    DTLZ2 benchmark problem

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

    g = np.sum((x[:, -k:] - 0.5) ** 2, axis=1)

    for i in range(numPop):

        for m in range(numObjectives):

            f = 1 + g[i]

            for j in range(numObjectives - m - 1):
                f *= np.cos(x[i, j] * np.pi / 2)

            if m > 0:
                f *= np.sin(x[i, numObjectives - m - 1] * np.pi / 2)

            fitness[i, m] = f

    return fitness

# ------------------------------------------------------------
# Plot Pareto Front
# ------------------------------------------------------------
def plot_pareto(fitness, num_points=4000):

    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    if fitness.shape[1] != 3:
        raise ValueError("DTLZ2 plot supports only 3 objectives")

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
    # TRUE Pareto Front (quarter sphere)
    # --------------------------------------------------------

    phi = np.random.uniform(0, np.pi / 2, num_points)
    theta = np.random.uniform(0, np.pi / 2, num_points)

    x = np.cos(phi) * np.cos(theta)
    y = np.cos(phi) * np.sin(theta)
    z = np.sin(phi)

    ax.scatter(
        x, y, z,
        alpha=0.15,
        label="True Pareto Front"
    )

    plt.gca().invert_yaxis()
    
    ax.set_xlabel("f1")
    ax.set_ylabel("f2")
    ax.set_zlabel("f3")

    ax.set_title("DTLZ2 Pareto Front")

    plt.legend()
    plt.show()


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():

    print("🚀 BQPhy Multi-Objective Optimization")
    print("📊 Benchmark: DTLZ2")
    print("=" * 60)

    numObjectives = 3

    config = {
        "numPopulation": 150,
        "maxGeneration": 500,
        "designVariables": numObjectives + 9,
        
        "typeOfOptimisation": "CONTINUOUS",

        "lowerBounds": [0.0] * (numObjectives + 9),
        "upperBounds": [1.0] * (numObjectives + 9),

        # Logging
        "outputFilePath": "dtlz2_results",
        "generationLogging": "noLogging",
    }

    # --------------------------------------------------------
    # Initialize optimizer
    # --------------------------------------------------------
    optimizer = qea.BQPhy_OPTIMISER()

    optimizer.initialize(config)

    optimizer.model(dtlz2)

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