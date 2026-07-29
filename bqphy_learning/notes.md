# BQPhy SDK Masterclass & Architecture Notes

## Overview
This document tracks our comprehensive, step-by-step mastery of the BQPhy SDK (Quantum-Inspired Evolutionary Optimization Toolkit by BosonQ Psi Corp).

---

## Completed Learning Steps

### Step 1: SDK Installation & Example Dissection (`step1_api_test.py`)
- **Key Takeaways**:
  - Python-C++ pybind11 bridge maps NumPy arrays directly into C++ core memory.
  - Vectorized fitness functions receive 2D candidate matrices of shape `(numPopulation, designVariables)`.
  - BQPhy minimizes scalar fitness scores; constraint violations are incorporated via penalty multipliers.

### Step 2: Standalone Task-Worker Assignment (`step2_binary_assignment.py`)
- **Key Takeaways**:
  - Multi-dimensional decision spaces (2D Task-Worker matrices) are flattened into 1D vectors for BQPhy and reshaped into 3D tensors `(numPopulation, Tasks, Workers)` inside Python using zero-copy NumPy views.
  - Formulated dual penalties: quadratic penalties for equality constraints ($(X_{assign} - 1)^2$) and linear excess penalties for workload capacity ($\max(Load - Capacity, 0)$).
  - Converged to global optimum in 3 generations.

### Step 3: Pure Quantum-Inspired Miniature CVRP (`step3_small_cvrp.py`)
- **Key Takeaways**:
  - Formulated routing as a 3D binary transition matrix tensor $X_{k, i, j} \in \{0, 1\}$ (50 binary decision variables across 2 vehicles and 5 nodes).
  - Fully vectorized flow conservation, self-loop elimination, capacity excess, customer visit uniqueness, and subtour depot connectivity checks using pure NumPy tensor math.
  - Decoded math into human-readable plain text and ASCII math formats.

---

## Step 4: Complete BQPhy Architecture & Comparative Benchmark Synthesis

### 1. Architectural Layers
```
[ Python User Script ]
        |  (Dict config, NumPy arrays, Callbacks)
        v
[ Pybind11 C++ Binding Layer ] (Zero-Copy Buffer Interface)
        |
        v
[ C++ QIEO Engine Core ] (BQPhy_Optimiser.pyd)
  ├── Q-bit Amplitude Vectors: |Psi_i> = alpha_i|0> + beta_i|1>
  ├── Quantum Rotation Gate Operator R(Delta_Theta)
  ├── Fitness Comparator & Global Best Tracker
  └── Multi-Thread Execution Layer (CPU / OpenMP / CUDA)
```

### 2. Paradigm Comparisons

| Dimension | BQPhy (Quantum-Inspired) | Simulated Annealing (SA) | QAOA (Gate-Based Quantum) | OR-Tools (Constraint Programming) |
| :--- | :--- | :--- | :--- | :--- |
| **Core Mechanism** | Q-bit superposition & Quantum Rotation Gates ($R(\Delta\theta)$) | Thermal state jumps & Boltzmann cooling schedule | Parametrized quantum circuits ($U(C, \gamma), U(B, \beta)$) | Arc consistency, domain reduction, branch-and-bound |
| **Execution Hardware** | Standard Classical CPU / OpenMP / GPU | Classical CPU | Physical Quantum Processor / Noisy Simulator | Classical CPU |
| **Population State** | Parallel Population of Q-bit probability amplitudes | Single solution state trajectory | Quantum state vector over $2^N$ Hilbert space | Tree search branches |
| **Constraint Handling** | Vectorized Penalty Functions in Fitness Callback | Penalty in cost function | QUBO / Ising Hamiltonian penalty terms | Native constraint declarations (e.g. `AddDimension`) |
| **Scalability** | High (handles thousands of binary variables on CPU/GPU) | High (fast single-state transitions) | Low (limited by noisy physical qubit counts) | Extremely High for exact routing |

---

## Final Readiness for GreenRoute Integration
1. Use OR-Tools for initial routing search or baseline constraints.
2. Use BQPhy's vectorized tensor penalty engine for quantum-inspired optimization, penalty tuning, and multi-objective Pareto refinement.
