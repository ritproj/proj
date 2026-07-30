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
BQPHY_POPULATION: int = 200
BQPHY_GENERATIONS: int = 800
BQPHY_DELTA_THETA: float = 0.12

# Maximum customers per direct BQPhy call before clustering kicks in.
# BQPhy handles larger problems than the SA solver, so the ceiling is raised.
# At N=16 customers and K=3 vehicles: 16×3=48 binary vars — well within reach.
BQPHY_CUSTOMER_LIMIT: int = 16

# Hard cap on binary variables BQPhy will optimise directly.
# At 128 vars: 8 customers × 16 vehicles or 16 customers × 8 vehicles.
BQPHY_QUBIT_LIMIT: int = 128

# Number of independent BQPhy restarts — best result is kept (like SA's N_RUNS=5).
# More runs = more reliable, but slower. 3 is a good hackathon balance.
BQPHY_RUNS: int = 3

# Set to "generationalLogging" to capture per-generation fitness CSV for convergence plots.
# Set to "noLogging" for production speed.
BQPHY_GEN_LOGGING: str = "noLogging"
