"""
distance.py — builds an (N+1) x (N+1) distance matrix.

Index 0 is always the depot.
Indices 1..N correspond to customers in the order they are passed.

Supports both Haversine (geographic, default) and Euclidean distance.
"""

from __future__ import annotations

import math
from typing import List

import numpy as np

from app.models.customer import Customer
from app.models.depot import Depot


# ---------------------------------------------------------------------------
# Haversine
# ---------------------------------------------------------------------------

_EARTH_RADIUS_KM = 6371.0


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres between two (lat, lon) points."""
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def _euclidean_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Simple Euclidean distance (degree-space).  Suitable for small areas."""
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_distance_matrix(
    depot: Depot,
    customers: List[Customer],
    use_haversine: bool = True,
) -> np.ndarray:
    """
    Build an (N+1) x (N+1) symmetric distance matrix.

    Row/column 0  → depot
    Row/column i  → customers[i-1]  (i = 1 … N)

    Parameters
    ----------
    depot : Depot
    customers : list[Customer]  (length N)
    use_haversine : bool
        True  → real-world km via Haversine (default)
        False → Euclidean in degree space (fast, good for unit tests)

    Returns
    -------
    numpy.ndarray  shape (N+1, N+1), dtype float64
    """
    dist_fn = _haversine_km if use_haversine else _euclidean_km

    # Build list of (lat, lon): depot first, then customers
    nodes = [(depot.latitude, depot.longitude)] + [
        (c.latitude, c.longitude) for c in customers
    ]
    n = len(nodes)
    matrix = np.zeros((n, n), dtype=np.float64)

    for i in range(n):
        for j in range(i + 1, n):
            d = dist_fn(nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1])
            matrix[i][j] = d
            matrix[j][i] = d

    return matrix


def matrix_to_int(matrix: np.ndarray, scale: int = 1000) -> List[List[int]]:
    """
    Convert a float distance matrix to integer (OR-Tools requires int).
    Multiplies by `scale` and rounds.
    """
    return (matrix * scale).round().astype(int).tolist()
