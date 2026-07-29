#!/usr/bin/env python3
"""
BQPhy Multi-Objective Optimization Example
Objectives:
1. Rastrigin function (multi-modal)
2. Sphere function (convex)
"""

import numpy as np
import bqphy.BQPhy_Optimiser as qea
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def animate_pareto_2d(fit_history, interval=200):
    fig, ax = plt.subplots()
    scat = ax.scatter([], [])

    ax.set_xlabel("Objective 1")
    ax.set_ylabel("Objective 2")
    ax.set_title("Pareto Front Evolution")

    def init():
        scat.set_offsets(np.empty((0, 2)))
        return scat,

    def update(frame):
        data = np.array(fit_history[frame])

        if data.shape[1] != 2:
            raise ValueError("This function supports only 2 objectives")

        scat.set_offsets(data)

        # Manual scaling (important!)
        ax.set_xlim(np.min(data[:, 0]), np.max(data[:, 0]))
        ax.set_ylim(np.min(data[:, 1]), np.max(data[:, 1]))

        ax.set_title(f"Generation {frame}")
        return scat,

    ani = FuncAnimation(
        fig,
        update,
        frames=len(fit_history),
        init_func=init,
        interval=interval,
        blit=False
    )

    plt.show()
    return ani

def plot_hypervolume(hv_values):
    import matplotlib.pyplot as plt

    plt.figure()
    plt.plot(hv_values, marker='o')
    plt.xlabel("Generation")
    plt.ylabel("Hypervolume")
    plt.title("Hypervolume Convergence")
    plt.grid(True)
    plt.show()


def hypervolume_2d(front, ref_point):
    """
    front: (N, 2) non-dominated points (minimization)
    ref_point: [r1, r2] (must dominate all points)
    """

    # Sort by first objective
    front = front[np.argsort(front[:, 0])]

    hv = 0.0
    prev_f1 = ref_point[0]

    for f1, f2 in reversed(front):
        width = prev_f1 - f1
        height = ref_point[1] - f2
        hv += width * height
        prev_f1 = f1

    return hv

def compute_hv_history(fit_history, ref_point):
    hv_values = []

    for gen, front in enumerate(fit_history):
        if front.shape[1] != 2:
            raise ValueError("Hypervolume function supports 2D only")

        hv = hypervolume_2d(front, ref_point)
        hv_values.append(hv)

    return np.array(hv_values)

def multi_objective_function(x):
    """
    Multi-objective function:
    f1 = Rastrigin
    f2 = Sphere
    
    Args:
        x: shape (population, designVariables)
    
    Returns:
        fitness: shape (population, 2)
    """
    A = 10
    numPop = x.shape[0]
    dim = x.shape[1]

    fitness = np.zeros((numPop, 2), dtype=np.float64)

    for i in range(numPop):
        xi = x[i]

        # Objective 1: Rastrigin
        f1 = A * dim + np.sum(xi**2 - A * np.cos(2 * np.pi * xi))

        # Objective 2: Sphere
        f2 = np.sum(xi**2)

        fitness[i, 0] = f1
        fitness[i, 1] = f2

    return fitness


def main():
    print("🚀 BQPhy Multi-Objective Optimization Example")
    print("📊 Problem: Rastrigin + Sphere")
    print("=" * 60)
    
    config = {
        "numPopulation": 15,
        "maxGeneration": 200,
        "deltaTheta": 0.05,
        "designVariables": 4,
        "typeOfOptimisation": "CONTINUOUS",

        # Bounds
        "lowerBounds": [-5.12] * 4,
        "upperBounds": [5.12] * 4,

        # Output
        "outputFilePath": "optimization_results_multi",
        "generationLogging": "noLogging",
    }

    optimizer = qea.BQPhy_OPTIMISER()
    optimizer.initialize(config)
    optimizer.model(multi_objective_function)

    print("⚡ Running optimization...")
    optimizer.runOptimization()

    best_solution, best_fitness = optimizer.getBestDesign()

    optimizer.writeCSV()

    print("\n" + "=" * 60)
    print("✅ Optimization Complete!")

    print(f"🎯 Best Solution: {[f'{x:.6f}' for x in best_solution]}")

    print("📈 Best Fitness (flattened):")
    print(best_fitness)

    # Extracting and printing Pareto front
    solutions, fitness = optimizer.getParetoFront()
    print("Solutions shape:", solutions.shape)  # (N, D)
    print("Solutions:", solutions)
    print("Fitness shape:", fitness.shape)      # (N, M)
    print("Multi-objective Fitness:", fitness)

    # Extracting and printing Pareto history
    sol_history, fit_history = optimizer.getParetoHistory()
    # for gen, (sol, fit) in enumerate(zip(sol_history, fit_history)):
    #     print(f"Generation {gen}:")
    #     print(" Solutions shape:", sol.shape)   # (numParetoPoints, dimension)
    #     print(" Fitness shape:", fit.shape)     # (numParetoPoints, numObjectives)

    # Convert to numpy (if not already)
    fit_history = [np.array(f) for f in fit_history]

    # # 🎬 Animate
    # animate_pareto_2d(fit_history)

    # 📈 Hypervolume
    ref_point = np.array([10.0, 10.0])  # must be worse than all points
    hv_values = compute_hv_history(fit_history, ref_point)

    plot_hypervolume(hv_values)

    print("\n💡 Note:")
    print("- Fitness is flattened: [f1_1, f2_1, f1_2, f2_2, ...]")
    print("- Pareto optimal solutions are expected near zero vector")


if __name__ == "__main__":
    main()