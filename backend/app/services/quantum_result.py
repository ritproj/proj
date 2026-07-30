from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

@dataclass
class QuantumResult:
    routes: List[List[int]]
    total_distance_km: float
    runtime_s: float
    feasible: bool
    fallback_used: bool
    objective_best: float
    objective_mean: float
    objective_variance: float
    runs: int
    n_vars: int
    method: str   # "exhaustive" | "simulated_annealing" | "nn_fallback" | "bqphy"
    distance_matrix: np.ndarray = field(repr=False)
    infeasible_reason: Optional[str] = None
