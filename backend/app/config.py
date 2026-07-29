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
