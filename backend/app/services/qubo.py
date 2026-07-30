"""
qubo.py — Assignment-variable QUBO for small CVRP instances.

Variable encoding
-----------------
y[i, k] = 1  if customer i is assigned to vehicle k
i ∈ {0 … N-1}  (customer index, 0-based)
k ∈ {0 … K-1}  (vehicle index, 0-based)

Total variables: N × K  (vs N²×K for arc-encoding — tractable on local simulator)

Objective
---------
H_distance ≈ Σ_k  route_cost(vehicle k's assigned customers)

Constraints (as squared-penalty additions)
-------------------------------------------
H_assign  : each customer assigned to exactly one vehicle
H_capacity: each vehicle's total load ≤ its capacity

Combined
--------
H = H_distance + λ·H_assign + λ·H_capacity
λ = PENALTY_MULTIPLIER × (max pairwise distance in km)
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from app.models.customer import Customer

# Penalty multiplier — λ = PENALTY_MULTIPLIER × max_edge_km × N_customers.
# Must be large enough that violating any constraint is always worse
# than any improvement to the objective. Raised from 10 → 50.
PENALTY_MULTIPLIER: float = 50.0

QUBODict = Dict[Tuple[int, int], float]


def _var(i: int, k: int, K: int) -> int:
    """Flat index for y[i, k]: customer i assigned to vehicle k."""
    return i * K + k


def variable_count(n_customers: int, n_vehicles: int) -> int:
    return n_customers * n_vehicles


# ---------------------------------------------------------------------------
# QUBO builder
# ---------------------------------------------------------------------------

def build_qubo(
    distance_matrix: np.ndarray,
    customers: List[Customer],
    n_vehicles: int,
    capacities: List[float],          # per-vehicle capacity list (length = n_vehicles)
    penalty_multiplier: float = PENALTY_MULTIPLIER,
) -> Tuple[QUBODict, int, float]:
    """
    Build the assignment-variable CVRP QUBO.

    Parameters
    ----------
    distance_matrix  : np.ndarray  shape (N+1, N+1), row/col 0 = depot
    customers        : list[Customer]  length N
    n_vehicles       : K
    capacities       : list[float]  length K, per-vehicle capacity
    penalty_multiplier : λ = multiplier × max_edge_weight

    Returns
    -------
    qubo    : QUBODict  { (var_a, var_b): coefficient }
    n_vars  : N × K
    penalty : penalty weight used
    """
    N = len(customers)
    K = n_vehicles

    if len(capacities) != K:
        raise ValueError(f"capacities list length {len(capacities)} ≠ n_vehicles {K}")

    max_edge = float(np.max(distance_matrix))
    # Scale penalty by N so it stays dominant for large problems:
    # even if every customer is saved by 2*max_edge, the constraint still wins.
    penalty  = penalty_multiplier * max_edge * max(N, 1) if max_edge > 0 else penalty_multiplier

    n_vars   = variable_count(N, K)
    Q: QUBODict = {}

    demands = [c.demand for c in customers]   # 0-based customer index
    max_demand = max(demands) if demands else 1.0  # for capacity scale normalisation

    def add(a: int, b: int, val: float) -> None:
        if abs(val) < 1e-12:
            return
        if a > b:
            a, b = b, a
        Q[(a, b)] = Q.get((a, b), 0.0) + val

    # ------------------------------------------------------------------
    # H_distance
    # Approximate contribution of assigning customer i to vehicle k as:
    #   cost_ik = distance(depot→i) + distance(i→depot)
    #           = 2 * dist[0][i+1]     (round-trip stub cost)
    # This is an underestimate but gives the correct relative ordering.
    # When multiple customers are assigned to the same vehicle the
    # pairwise savings term is subtracted.
    # ------------------------------------------------------------------
    for i in range(N):
        node_i = i + 1  # node index in distance matrix (0 = depot)
        stub_i = distance_matrix[0][node_i] + distance_matrix[node_i][0]
        for k in range(K):
            v = _var(i, k, K)
            add(v, v, stub_i)

    # Pairwise savings when two customers share a vehicle:
    # saving(i,j) = dist[0,i] + dist[i,j] + dist[j,0]  (tour i→j)
    #             - dist[0,i] - dist[i,0]               (stub i)
    #             - dist[0,j] - dist[j,0]               (stub j)
    # = dist[i,j] - dist[i,0] - dist[0,j]
    # (negative saving = positive QUBO coefficient → penalise bad pairing)
    for i in range(N):
        for j in range(i + 1, N):
            ni, nj = i + 1, j + 1
            saving = distance_matrix[ni][nj] - distance_matrix[ni][0] - distance_matrix[0][nj]
            for k in range(K):
                vi = _var(i, k, K)
                vj = _var(j, k, K)
                # Both assigned to same vehicle: add saving (can be negative)
                add(vi, vj, saving)

    # ------------------------------------------------------------------
    # H_assign: each customer assigned to exactly one vehicle
    # (1 - Σ_k y[i,k])² for each i
    # = 1 - 2*Σ_k y[i,k] + (Σ_k y[i,k])²
    # Linear:    -2*penalty on each y[i,k]
    # Quadratic: +2*penalty on each pair (y[i,k1], y[i,k2]), k1≠k2
    # ------------------------------------------------------------------
    for i in range(N):
        for k in range(K):
            v = _var(i, k, K)
            add(v, v, -2.0 * penalty)
        for k1 in range(K):
            for k2 in range(k1 + 1, K):
                add(_var(i, k1, K), _var(i, k2, K), 2.0 * penalty)

    # ------------------------------------------------------------------
    # H_capacity: Σ_i demand[i]*y[i,k] ≤ Q_k  for each k
    # Soft penalty via (Σ_i demand[i]*y[i,k] - Q_k)²
    #
    # Expand: Σ_i d_i² y_i (binary: y²=y, so diagonal)
    #       + 2*Σ_{i<j} d_i*d_j * y_i*y_j   (cross terms)
    #       - 2*Q_k * Σ_i d_i * y_i          (linear)
    #       + Q_k²                            (constant, ignored)
    #
    # Scale by penalty / max_demand² so the capacity penalty is always
    # comparable to the assignment penalty, regardless of vehicle size.
    # (Old: scale = penalty/Qk² — vanished for large Qk e.g. 9999 kg).
    # ------------------------------------------------------------------
    cap_scale = penalty / (max_demand ** 2) if max_demand > 0 else penalty

    for k in range(K):
        Qk = capacities[k]

        for i in range(N):
            v = _var(i, k, K)
            # diagonal: d_i² - 2*Q_k*d_i  (scaled)
            add(v, v, cap_scale * (demands[i] ** 2 - 2.0 * Qk * demands[i]))

        for i in range(N):
            for j in range(i + 1, N):
                vi = _var(i, k, K)
                vj = _var(j, k, K)
                add(vi, vj, cap_scale * 2.0 * demands[i] * demands[j])

    return Q, n_vars, penalty
