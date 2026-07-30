"""
config.py — single source of truth for all constants.
Import from here, not from individual service files.
"""

DEBUG: bool = False

# Maximum customers before quantum clustering notice is shown
# (must match QAOA_CUSTOMER_LIMIT in qaoa_solver.py)
QAOA_CUSTOMER_LIMIT: int = 8

# Decision Engine weights (ADR-003)
# 0.75 distance / 0.25 runtime — distance is the primary optimisation target.
DECISION_DISTANCE_WEIGHT: float = 0.75
DECISION_RUNTIME_WEIGHT:  float = 0.25
assert abs(DECISION_DISTANCE_WEIGHT + DECISION_RUNTIME_WEIGHT - 1.0) < 1e-9, \
    "Decision weights must sum to 1.0"

# Clustering gate
ENABLE_LIVE_CLUSTERING: bool = True

QUANTUM_SOLVER_BACKEND: str = "bqphy"

# BQPhy specific hyperparameters
# These are the base values for small problems (n_vars ≤ 30).
# The solver auto-scales population and generations for larger problems.
BQPHY_POPULATION: int = 200
BQPHY_GENERATIONS: int = 800
BQPHY_DELTA_THETA: float = 0.12

# Maximum customers per direct BQPhy call before clustering kicks in.
# BQPhy handles large QUBO matrices efficiently — 50 customers is well within reach.
# At N=50 customers and K=4 vehicles: 50×4=200 binary vars — fully supported.
BQPHY_CUSTOMER_LIMIT: int = 50

# Hard cap on binary variables BQPhy will optimise directly.
# Raised to 500: this covers 50 customers × 10 vehicles without clamping vehicles.
BQPHY_QUBIT_LIMIT: int = 500

# Number of independent BQPhy restarts — best result is kept.
# 3 restarts is reliable for small/medium problems.
# The solver auto-increases this for small problems (fast runs).
BQPHY_RUNS: int = 3

# Set to "generationalLogging" to capture per-generation fitness CSV for convergence plots.
# Set to "noLogging" for production speed.
BQPHY_GEN_LOGGING: str = "noLogging"
