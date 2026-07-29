"""
repair.py — decode QAOA bitstring → routes, validate, repair, fallback.

New variable encoding: y[i,k] = customer i assigned to vehicle k.
Flat index: i*K + k   (N×K total variables)
"""
from __future__ import annotations

from typing import List, Optional, Tuple
import numpy as np

from app.models.customer import Customer


# ---------------------------------------------------------------------------
# 1. Decode assignment bitstring → routes
# ---------------------------------------------------------------------------

def decode_bitstring(
    bitstring: str,
    customers: List[Customer],
    n_vehicles: int,
    distance_matrix: np.ndarray,
    capacities: List[float],
) -> List[List[int]]:
    """
    Decode y[i,k] bitstring into vehicle routes.

    For each vehicle k, collect assigned customers then build a
    nearest-neighbour tour starting and ending at depot (node 0).

    Returns list of routes, each route a list of node indices
    (0 = depot at start and end).
    """
    N = len(customers)
    K = n_vehicles
    bits = [int(b) for b in bitstring]

    # Group customers by vehicle
    vehicle_customers: List[List[int]] = [[] for _ in range(K)]
    for i in range(N):
        for k in range(K):
            idx = i * K + k
            if idx < len(bits) and bits[idx] == 1:
                vehicle_customers[k].append(i + 1)   # node index (1-based)

    routes: List[List[int]] = []
    for k, assigned in enumerate(vehicle_customers):
        if not assigned:
            routes.append([0, 0])
            continue
        # Build NN tour over assigned customers
        route = [0]
        unvisited = list(assigned)
        current = 0
        while unvisited:
            nearest = min(unvisited, key=lambda j: distance_matrix[current][j])
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        route.append(0)
        routes.append(route)

    return routes


# ---------------------------------------------------------------------------
# 2. Validate routes
# ---------------------------------------------------------------------------

def validate_routes(
    routes: List[List[int]],
    customers: List[Customer],
    capacities: List[float],          # per-vehicle capacity, length = len(routes) max
) -> Tuple[bool, List[str]]:
    """
    Check:
      - Every customer visited exactly once.
      - No vehicle exceeds its capacity.
      - Every route starts and ends at depot (node 0).

    capacities[k] is the capacity for the k-th *non-empty* route.
    If fewer capacities provided than routes, the last value is reused.
    """
    violations: List[str] = []
    if len(routes) > len(capacities):
        violations.append(f"Fleet constraint violated: {len(routes)} routes generated, but only {len(capacities)} vehicles available.")

    n_customers = len(customers)
    demands = {i + 1: c.demand for i, c in enumerate(customers)}
    visit_count = {i + 1: 0 for i in range(n_customers)}

    for v_idx, route in enumerate(routes):
        if not route or route[0] != 0 or route[-1] != 0:
            violations.append(f"Vehicle {v_idx}: route does not start/end at depot.")

        cap = capacities[v_idx] if v_idx < len(capacities) else capacities[-1]
        load = 0.0
        for node in route:
            if node == 0:
                continue
            visit_count[node] = visit_count.get(node, 0) + 1
            load += demands.get(node, 0)

        if load > cap + 1e-6:
            violations.append(
                f"Vehicle {v_idx}: capacity exceeded ({load:.1f} > {cap:.1f})."
            )

    for node, count in visit_count.items():
        if count == 0:
            violations.append(f"Customer node {node} not visited.")
        elif count > 1:
            violations.append(f"Customer node {node} visited {count} times.")

    return len(violations) == 0, violations


# ---------------------------------------------------------------------------
# 3. Greedy repair
# ---------------------------------------------------------------------------

def repair_routes(
    routes: List[List[int]],
    customers: List[Customer],
    capacities: List[float],
    distance_matrix: np.ndarray,
) -> Tuple[List[List[int]], bool]:
    """
    Fix infeasible routes:
      - Remove duplicate visits.
      - Insert missing customers into cheapest feasible position.
    """
    n_customers = len(customers)
    demands = {i + 1: c.demand for i, c in enumerate(customers)}

    def cap_for(r_idx: int) -> float:
        return capacities[r_idx] if r_idx < len(capacities) else capacities[-1]

    # Remove duplicates
    seen: set = set()
    cleaned: List[List[int]] = []
    for route in routes:
        new_route = [0]
        for node in route[1:-1]:
            if node not in seen:
                new_route.append(node)
                seen.add(node)
        new_route.append(0)
        cleaned.append(new_route)

    # Find unvisited
    unvisited = set(range(1, n_customers + 1)) - seen

    # Insert each unvisited into cheapest feasible position
    for node in unvisited:
        best_cost, best_r, best_pos = float("inf"), -1, -1
        for r_idx, route in enumerate(cleaned):
            load = sum(demands.get(n, 0) for n in route)
            if load + demands[node] > cap_for(r_idx) + 1e-6:
                continue
            for pos in range(1, len(route)):
                prev, nxt = route[pos - 1], route[pos]
                cost = (distance_matrix[prev][node]
                        + distance_matrix[node][nxt]
                        - distance_matrix[prev][nxt])
                if cost < best_cost:
                    best_cost, best_r, best_pos = cost, r_idx, pos
        if best_r >= 0:
            cleaned[best_r].insert(best_pos, node)
        # If best_r < 0, the node cannot fit anywhere without violating capacity.
        # We simply leave it unassigned. validate_routes() will flag it as unvisited.

    feasible, _ = validate_routes(cleaned, customers, capacities)
    return cleaned, feasible


# ---------------------------------------------------------------------------
# 4. Nearest-neighbour fallback heuristic
# ---------------------------------------------------------------------------

def nearest_neighbor_heuristic(
    distance_matrix: np.ndarray,
    customers: List[Customer],
    n_vehicles: int,
    capacities: List[float],
) -> List[List[int]]:
    """
    Nearest-neighbour heuristic.  Vehicle k has capacity capacities[k].
    """
    demands = {i + 1: c.demand for i, c in enumerate(customers)}
    unvisited = set(range(1, len(customers) + 1))
    routes: List[List[int]] = []

    for k in range(n_vehicles):
        if not unvisited:
            break
        cap = capacities[k] if k < len(capacities) else capacities[-1]
        route = [0]
        current, load = 0, 0.0

        while unvisited:
            best_node: Optional[int] = None
            best_dist = float("inf")
            for node in unvisited:
                if load + demands[node] <= cap + 1e-6:
                    d = distance_matrix[current][node]
                    if d < best_dist:
                        best_dist, best_node = d, node
            if best_node is None:
                break
            route.append(best_node)
            unvisited.remove(best_node)
            load += demands[best_node]
            current = best_node

        route.append(0)
        routes.append(route)

    # Do not append extra vehicles for unvisited nodes. 
    # Let validate_routes() catch the unvisited nodes and fail properly.

    return routes


# ---------------------------------------------------------------------------
# 5. 2-opt local search (per-route improvement)
# ---------------------------------------------------------------------------

def two_opt_improve(
    routes: List[List[int]],
    distance_matrix: np.ndarray,
    max_iter: int = 100,
) -> List[List[int]]:
    """
    Apply 2-opt improvement to each route independently.
    Only swaps the customer segment (keeps depot at start/end).
    Runs until no improvement or max_iter reached.
    """
    improved_routes = []
    for route in routes:
        # route = [0, c1, c2, ..., cn, 0]
        if len(route) <= 3:          # 0 or 1 customer — nothing to swap
            improved_routes.append(route)
            continue

        best = list(route)
        for _ in range(max_iter):
            improved = False
            # Segment indices: 1 .. len-2 (exclude depot endpoints)
            n = len(best)
            for i in range(1, n - 2):
                for j in range(i + 1, n - 1):
                    # Current edges: (best[i-1]→best[i]) and (best[j]→best[j+1])
                    # After swap:    (best[i-1]→best[j]) and (best[i]→best[j+1])
                    d_before = (distance_matrix[best[i - 1]][best[i]]
                                + distance_matrix[best[j]][best[j + 1]])
                    d_after  = (distance_matrix[best[i - 1]][best[j]]
                                + distance_matrix[best[i]][best[j + 1]])
                    if d_after < d_before - 1e-9:
                        best[i:j + 1] = best[i:j + 1][::-1]
                        improved = True
            if not improved:
                break
        improved_routes.append(best)
    return improved_routes


def nearest_neighbor_with_2opt(
    distance_matrix: np.ndarray,
    customers: List[Customer],
    n_vehicles: int,
    capacities: List[float],
) -> List[List[int]]:
    """NN construction + 2-opt improvement — used as the quantum fallback."""
    routes = nearest_neighbor_heuristic(distance_matrix, customers, n_vehicles, capacities)
    return two_opt_improve(routes, distance_matrix)
