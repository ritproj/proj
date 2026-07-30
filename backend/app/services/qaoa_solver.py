"""
qaoa_solver.py — QUBO-based CVRP solver with multi-run benchmarking.

Variable encoding: y[i,k] = 1 if customer i assigned to vehicle k  (N×K binary variables).
For 6 customers + 2 vehicles = 12 variables — tractable on any machine.

Solver strategy (chosen based on problem size)
----------------------------------------------
n_vars ≤ 16  : Exhaustive enumeration — exact global optimum, fast (2^16 = 65 536 evals)
17–24        : Simulated Annealing — N_RUNS independent restarts, best result kept
> 24         : NN + 2-opt fallback (labelled fallback_used=True in response)

Runs: N_RUNS=5 independent SA restarts; mean and variance of objectives reported.
Fallback: nearest-neighbour + 2-opt when QUBO is too large or N > QAOA_CUSTOMER_LIMIT.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from app.services.quantum_result import QuantumResult
from app.services.base_solver import BaseQuantumSolver

from typing import Dict, List, Optional, Tuple

import numpy as np

from app.services.fitness import evaluate_qubo_energy


from app.models.customer import Customer
from app.models.depot import Depot
from app.models.vehicle import VehicleConfig
from app.services.distance import build_distance_matrix
from app.services.qubo import build_qubo, variable_count
from app.services.repair import (
    decode_bitstring,
    nearest_neighbor_heuristic,
    nearest_neighbor_with_2opt,
    repair_routes,
    two_opt_improve,
    validate_routes,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
QAOA_LAYERS          = 2      # p=2 is sufficient for small instances
N_RUNS               = 5      # independent SA restarts — best result selected, mean/variance reported
MAX_SHOTS            = 1024
MAX_ITER             = 150    # COBYLA iterations
QAOA_CUSTOMER_LIMIT  = 8      # customers accepted before clustering kicks in
QAOA_QUBIT_LIMIT     = 24     # n_vars limit: ≤16 → exhaustive, 17-24 → SA, >24 → NN+2opt



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _qubo_to_matrix(qubo: Dict, n_vars: int) -> np.ndarray:
    Q = np.zeros((n_vars, n_vars), dtype=np.float64)
    for (i, j), val in qubo.items():
        Q[i][j] += val
        if i != j:
            Q[j][i] += val
    return Q


def _eval_bitstring(bitstring: str, Q: np.ndarray) -> float:
    x = np.array([int(b) for b in bitstring], dtype=np.float64)
    return float(x @ Q @ x)


def _run_single_qaoa(Q_matrix: np.ndarray, n_vars: int) -> Tuple[str, float, float]:
    """
    Solve the QUBO:
    - n_vars ≤ 16: exhaustive enumeration (exact, fast — 2^16 = 65536 evaluations)
    - 16 < n_vars ≤ QAOA_QUBIT_LIMIT: Simulated Annealing (heuristic, fast)
    - n_vars > QAOA_QUBIT_LIMIT: raise ValueError → caller uses NN+2opt

    Raises ValueError if n_vars > QAOA_QUBIT_LIMIT.
    """
    t0 = time.perf_counter()

    if n_vars > QAOA_QUBIT_LIMIT:
        raise ValueError(f"QUBO has {n_vars} variables — exceeds {QAOA_QUBIT_LIMIT}-qubit limit.")

    best_bs  = None
    best_obj = float("inf")

    if n_vars <= 16:
        # ── Exhaustive enumeration ──────────────────────────────────────
        for bits in range(2 ** n_vars):
            x   = np.array([(bits >> i) & 1 for i in range(n_vars)], dtype=np.float64)
            obj = float(x @ Q_matrix @ x)
            if obj < best_obj:
                best_obj = obj
                best_bs  = "".join(str(int(b)) for b in x)
    else:
        # ── Simulated Annealing ─────────────────────────────────────────
        rng = np.random.default_rng()

        def energy(x: np.ndarray) -> float:
            return evaluate_qubo_energy(x, Q_matrix)

        for _ in range(N_RUNS * 4):
            x      = rng.integers(0, 2, size=n_vars).astype(np.float64)
            T      = 3.0
            T_min  = 1e-4
            alpha  = 0.92
            e      = energy(x)
            x_best = x.copy()
            e_best = e

            while T > T_min:
                i        = int(rng.integers(n_vars))
                x_new    = x.copy()
                x_new[i] = 1.0 - x_new[i]
                e_new    = energy(x_new)
                delta    = e_new - e
                if delta < 0 or rng.random() < np.exp(-delta / T):
                    x, e = x_new, e_new
                    if e < e_best:
                        x_best, e_best = x.copy(), e
                T *= alpha

            bs = "".join(str(int(b)) for b in x_best)
            if e_best < best_obj:
                best_obj, best_bs = e_best, bs

    return best_bs, best_obj, time.perf_counter() - t0


# ---------------------------------------------------------------------------
# Public solver
# ---------------------------------------------------------------------------

def _internal_solve_quantum(
    depot: Depot,
    customers: List[Customer],
    vehicle_config: VehicleConfig,
    bypass_clustering: bool = False,
) -> QuantumResult:
    dist_matrix = build_distance_matrix(depot, customers)
    K           = vehicle_config.total_count
    cap_list    = vehicle_config.capacities_list   # per-vehicle, length K

    # ── Upfront Feasibility Guard ──────────────────
    total_demand = sum(c.demand for c in customers)
    total_cap = sum(cap_list)
    max_demand = max([c.demand for c in customers], default=0)
    max_cap = max(cap_list, default=0)

    if total_demand > total_cap + 1e-6:
        return QuantumResult(
            routes=[], total_distance_km=0.0, runtime_s=0.0,
            feasible=False, fallback_used=False,
            objective_best=0.0, objective_mean=0.0, objective_variance=0.0,
            runs=0, n_vars=0, method="none", distance_matrix=dist_matrix,
            infeasible_reason="TOTAL_DEMAND_EXCEEDS_FLEET_CAPACITY"
        )
    if max_demand > max_cap + 1e-6:
        return QuantumResult(
            routes=[], total_distance_km=0.0, runtime_s=0.0,
            feasible=False, fallback_used=False,
            objective_best=0.0, objective_mean=0.0, objective_variance=0.0,
            runs=0, n_vars=0, method="none", distance_matrix=dist_matrix,
            infeasible_reason="CUSTOMER_EXCEEDS_MAX_VEHICLE_CAPACITY"
        )

    # ── Hard cap: cluster customers for large instances ──────────────────
    if len(customers) > QAOA_CUSTOMER_LIMIT and not bypass_clustering:
        return _solve_clustered_quantum(depot, customers, vehicle_config)

    # ── Clamp vehicle count so N × K_qaoa ≤ QAOA_QUBIT_LIMIT ────────────
    N        = len(customers)
    K_qaoa   = min(K, QAOA_QUBIT_LIMIT // N) if N > 0 else K
    K_qaoa   = max(K_qaoa, 1)

    # ── Build QUBO ──────────────────────────────────────────────────────
    qubo_dict, n_vars, _ = build_qubo(
        distance_matrix=dist_matrix,
        customers=customers,
        n_vehicles=K_qaoa,
        capacities=cap_list[:K_qaoa],
    )
    Q_matrix = _qubo_to_matrix(qubo_dict, n_vars)

    # ── QUBO optimisation — N_RUNS independent SA restarts ──────────────
    objectives: List[float] = []
    runtimes:   List[float] = []
    best_bs:  Optional[str] = None
    best_obj               = float("inf")

    for _ in range(N_RUNS):
        try:
            bs, obj, rt = _run_single_qaoa(Q_matrix, n_vars)
        except ValueError:
            break   # n_vars too large → fall through to NN+2opt
        objectives.append(obj)
        runtimes.append(rt)
        if obj < best_obj:
            best_obj, best_bs = obj, bs

    # ── No QAOA run succeeded ───────────────────────────────────────────
    if not best_bs:
        return _nn_result(dist_matrix, customers, K, cap_list, fallback=True, runs=0)

    total_rt = sum(runtimes)
    obj_mean = float(np.mean(objectives))
    obj_var  = float(np.var(objectives))

    # ── Decode bitstring → routes ───────────────────────────────────────
    routes = decode_bitstring(best_bs, customers, K_qaoa, dist_matrix, cap_list[:K_qaoa])


    print("\n========== AFTER DECODE ==========")
    print("Original vehicles (K):", K)
    print("QAOA vehicles (K_qaoa):", K_qaoa)
    print("Capacities:", cap_list[:K_qaoa])

    print("Number of decoded routes:", len(routes))

    for i, r in enumerate(routes):
        print(f"Route {i+1}: {r}")

    print("==================================\n")



    # ── Validate → repair → NN+2opt fallback ───────────────────────────
    feasible, _     = validate_routes(routes, customers, cap_list[:K_qaoa])
    fallback_used   = False

    if not feasible:
        routes, feasible = repair_routes(routes, customers, cap_list[:K_qaoa], dist_matrix)

    if not feasible:
        routes        = nearest_neighbor_with_2opt(dist_matrix, customers, K, cap_list)
        feasible, _   = validate_routes(routes, customers, cap_list)
        fallback_used = True
    else:
        # Apply 2-opt to improve the QAOA-decoded routes too
        routes = two_opt_improve(routes, dist_matrix)

    # ── Final Safety Check ─────────────────────────────
    final_feasible, _ = validate_routes(routes, customers, cap_list)
    if not final_feasible:
        feasible = False

    print("\n========== FINAL ROUTES ==========")
    print("Number of final routes:", len(routes))

    for i, r in enumerate(routes):
        print(f"Final Route {i+1}: {r}")

    print("==================================\n")


    total_km = _total_dist(routes, dist_matrix)

    reason = None
    if not feasible:
        reason = "CAPACITY_VIOLATION_AFTER_REPAIR"

    return QuantumResult(
        routes=routes,
        total_distance_km=round(float(total_km), 3),
        runtime_s=round(total_rt, 4),
        feasible=feasible,
        fallback_used=fallback_used,
        objective_best=round(best_obj, 4),
        objective_mean=round(obj_mean, 4),
        objective_variance=round(obj_var, 4),
        runs=len(objectives),
        n_vars=n_vars,
        method="exhaustive" if n_vars <= 16 else "simulated_annealing",
        distance_matrix=dist_matrix,
        infeasible_reason=reason
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _solve_clustered_quantum(
    depot: Depot,
    customers: List[Customer],
    vehicle_config: VehicleConfig,
) -> QuantumResult:
    dist_matrix = build_distance_matrix(depot, customers)
    K = vehicle_config.total_count
    cap_list = vehicle_config.capacities_list  # length K; cap_list[k] = vehicle k's capacity

    # ── Upfront Feasibility Guard ──────────────────
    total_demand = sum(c.demand for c in customers)
    total_cap = sum(cap_list)
    max_demand = max([c.demand for c in customers], default=0)
    max_cap = max(cap_list, default=0)

    if total_demand > total_cap + 1e-6:
        return QuantumResult(
            routes=[], total_distance_km=0.0, runtime_s=0.0,
            feasible=False, fallback_used=False,
            objective_best=0.0, objective_mean=0.0, objective_variance=0.0,
            runs=0, n_vars=0, method="none", distance_matrix=dist_matrix,
            infeasible_reason="TOTAL_DEMAND_EXCEEDS_FLEET_CAPACITY"
        )
    if max_demand > max_cap + 1e-6:
        return QuantumResult(
            routes=[], total_distance_km=0.0, runtime_s=0.0,
            feasible=False, fallback_used=False,
            objective_best=0.0, objective_mean=0.0, objective_variance=0.0,
            runs=0, n_vars=0, method="none", distance_matrix=dist_matrix,
            infeasible_reason="CUSTOMER_EXCEEDS_MAX_VEHICLE_CAPACITY"
        )

    # ── Step 1: Fleet-first cluster count ────────────────────────────────
    # Never create more clusters than we have vehicles.
    n_clusters = (len(customers) + QAOA_CUSTOMER_LIMIT - 1) // QAOA_CUSTOMER_LIMIT
    n_clusters = max(1, min(n_clusters, K))

    from app.services.dataset import cluster_customers
    geo_clusters = cluster_customers(customers, n_clusters)
    n_clusters = len(geo_clusters)  # actual clusters returned (may be < requested)

    print(f"\n========== CLUSTER DEBUG ==========")
    print(f"Total customers  : {len(customers)}")
    print(f"Fleet size (K)   : {K}")
    print(f"Geo-clusters     : {n_clusters}")

    # ── Step 2: Globally assign all K vehicles across clusters ────────────
    # Sort vehicles largest-first; sort clusters by total demand desc.
    # Phase A: give 1 vehicle per cluster (highest-demand → largest vehicle).
    # Phase B: assign remaining vehicles to clusters with most unmet demand.
    vehicles = sorted(
        [{"capacity": cap, "type": vtype, "global_idx": i}
         for i, (cap, vtype) in enumerate(zip(cap_list, vehicle_config.vehicle_types_list))],
        key=lambda v: v["capacity"],
        reverse=True,
    )
    cluster_demands = [sum(c.demand for c in cl) for cl in geo_clusters]
    demand_order = list(np.argsort(cluster_demands)[::-1])

    allocations: List[List[dict]] = [[] for _ in range(n_clusters)]
    pool = list(vehicles)

    # Phase A — one vehicle to each cluster
    for idx in demand_order:
        if pool:
            allocations[idx].append(pool.pop(0))

    # Phase B — distribute remaining vehicles to most-unmet-demand cluster
    while pool:
        veh = pool.pop(0)
        unsatisfied = [
            cluster_demands[i] - sum(v["capacity"] for v in allocations[i])
            for i in range(n_clusters)
        ]
        allocations[int(np.argmax(unsatisfied))].append(veh)

    # Invariant: sum of allocated == K
    assert sum(len(a) for a in allocations) == K, "BUG: vehicle allocation sum != K"

    # ── Step 3: Build per-cluster VehicleConfig ───────────────────────────
    cluster_configs: List[VehicleConfig] = []
    for alloc in allocations:
        fleet_dict:  Dict[str, int]   = {}
        caps_dict:   Dict[str, float] = {}
        for veh in alloc:
            vt = veh["type"]
            fleet_dict[vt] = fleet_dict.get(vt, 0) + 1
            caps_dict[vt]  = veh["capacity"]
        cluster_configs.append(VehicleConfig(fleet=fleet_dict, capacities=caps_dict))

    # ── Step 4: Solve each cluster; place routes into fixed vehicle slots ──
    # vehicle_routes[k] = the route owned by global vehicle k (None = empty).
    vehicle_routes: List[Optional[List[int]]] = [None] * K

    runtimes:         List[float] = []
    objectives_best:  List[float] = []
    objectives_mean:  List[float] = []
    objectives_var:   List[float] = []
    feasible_all      = True
    fallback_used_all = False
    methods: set      = set()
    max_vars          = 0

    for cl_idx, (cl, cl_cfg) in enumerate(zip(geo_clusters, cluster_configs)):
        ki  = cl_cfg.total_count   # vehicles dedicated to this cluster
        res = _internal_solve_quantum(depot, cl, cl_cfg, bypass_clustering=True)

        runtimes.append(res.runtime_s)
        objectives_best.append(res.objective_best)
        objectives_mean.append(res.objective_mean)
        objectives_var.append(res.objective_variance)
        if not res.feasible:
            feasible_all = False
        if res.fallback_used:
            fallback_used_all = True
        methods.add(res.method)
        max_vars = max(max_vars, res.n_vars)

        # Group the available global indices for this cluster by vehicle type
        available_global_indices = {}
        for veh in allocations[cl_idx]:
            available_global_indices.setdefault(veh["type"], []).append(veh["global_idx"])
            
        # Place mapped routes into the exact global index corresponding to their type
        for i, r in enumerate(res.routes):
            # Re-map this specific route's local indices to global customers
            m: List[int] = []
            for node in r:
                if node == 0:
                    m.append(0)
                else:
                    orig_idx = customers.index(cl[node - 1]) + 1
                    m.append(orig_idx)
            
            if len(m) > 2:
                # Get the vehicle type this route was solved for
                vtype = cl_cfg.vehicle_types_list[i]
                # Assign it to a global vehicle of that exact type
                global_idx = available_global_indices[vtype].pop(0)
                vehicle_routes[global_idx] = m

    # ── Step 5: Flatten; recover any missing customers ────────────────────
    # Preserve unused vehicles as empty routes to maintain 1-to-1 API global mapping.
    combined_routes = []
    final_caps = []
    for idx, r in enumerate(vehicle_routes):
        if r is not None:
            combined_routes.append(r)
        else:
            combined_routes.append([0, 0])
        final_caps.append(cap_list[idx])

    visited_so_far = {node for r in combined_routes for node in r if node != 0}
    missing_nodes  = [i + 1 for i in range(len(customers)) if (i + 1) not in visited_so_far]

    if missing_nodes:
        demands_map = {i + 1: c.demand for i, c in enumerate(customers)}
        for node in missing_nodes:
            best_cost, best_r, best_pos = float("inf"), -1, -1
            for r_idx, route in enumerate(combined_routes):
                slot_cap   = final_caps[r_idx] if r_idx < len(final_caps) else cap_list[-1]
                route_load = sum(demands_map.get(n, 0) for n in route if n != 0)
                if route_load + demands_map[node] > slot_cap + 1e-6:
                    continue
                
                for pos in range(1, len(route)):
                    # Evaluate insertion cost
                    prev_n = route[pos - 1]
                    next_n = route[pos]
                    cost   = dist_matrix[prev_n, node] + dist_matrix[node, next_n] - dist_matrix[prev_n, next_n]
                    if cost < best_cost:
                        best_cost, best_r, best_pos = cost, r_idx, pos
            if best_r >= 0:
                combined_routes[best_r].insert(best_pos, node)
            elif len(combined_routes) < K:
                combined_routes.append([0, node, 0])
            else:
                # Force into least-loaded route (capacity violation < missing customer)
                loads = [sum(demands_map.get(n, 0) for n in r if n != 0)
                         for r in combined_routes]
                combined_routes[int(np.argmin(loads))].insert(-1, node)

    # Ensure every route has proper depot bookends
    for r in combined_routes:
        if not r or r[0] != 0:
            r.insert(0, 0)
        if r[-1] != 0:
            r.append(0)

    if not combined_routes:
        combined_routes = [[0, 0]]

    # ── Step 6: Full CVRP validation ──────────────────────────────────────
    final_feasible, _ = validate_routes(combined_routes, customers, cap_list)
    if len(combined_routes) > K:
        final_feasible = False
        
    if not final_feasible:
        feasible_all = False

    # ── Step 7: 2-opt improvement ─────────────────────────────────────────
    combined_routes = two_opt_improve(combined_routes, dist_matrix)

    total_km = _total_dist(combined_routes, dist_matrix)

    if "nn_fallback" in methods:
        method = "nn_fallback"
    elif "simulated_annealing" in methods:
        method = "simulated_annealing"
    else:
        method = "exhaustive"

    print(f"Number of combined routes : {len(combined_routes)}")
    for i, r in enumerate(combined_routes):
        print(f"  Route {i + 1}: {r}")
    print("===================================\n")

    reason = None
    if not feasible_all:
        reason = "ROUTE_VALIDATION_FAILED"

    return QuantumResult(
        routes=combined_routes,
        total_distance_km=round(float(total_km), 3),
        runtime_s=round(sum(runtimes), 4),
        feasible=feasible_all,
        fallback_used=fallback_used_all,
        objective_best=round(sum(objectives_best), 4),
        objective_mean=round(sum(objectives_mean), 4),
        objective_variance=round(float(np.mean(objectives_var)), 4),
        runs=N_RUNS,
        n_vars=max_vars,
        method=method,
        distance_matrix=dist_matrix,
        infeasible_reason=reason
    )



def _nn_result(
    dist_matrix: np.ndarray,
    customers: List[Customer],
    K: int,
    cap_list: List[float],
    fallback: bool,
    runs: int,
) -> QuantumResult:
    t0     = time.perf_counter()
    routes = nearest_neighbor_with_2opt(dist_matrix, customers, K, cap_list)
    rt     = time.perf_counter() - t0
    km     = _total_dist(routes, dist_matrix)
    
    feasible, _ = validate_routes(routes, customers, cap_list)
    reason = None if feasible else "ROUTE_VALIDATION_FAILED"

    return QuantumResult(
        routes=routes,
        total_distance_km=round(float(km), 3),
        runtime_s=round(rt, 4),
        feasible=feasible,
        fallback_used=fallback,
        objective_best=round(float(km), 4),
        objective_mean=round(float(km), 4),
        objective_variance=0.0,
        runs=runs,
        n_vars=0,
        method="nn_fallback",
        distance_matrix=dist_matrix,
        infeasible_reason=reason
    )


def _total_dist(routes: List[List[int]], matrix: np.ndarray) -> float:
    return sum(matrix[a][b] for r in routes for a, b in zip(r, r[1:]))


class QAOASolver(BaseQuantumSolver):
    def solve(
        self,
        depot: Depot,
        customers: List[Customer],
        vehicle_config: VehicleConfig,
        bypass_clustering: bool = False,
    ) -> QuantumResult:
        return _internal_solve_quantum(depot, customers, vehicle_config, bypass_clustering)

def solve_quantum(
    depot: Depot,
    customers: List[Customer],
    vehicle_config: VehicleConfig,
    bypass_clustering: bool = False,
) -> QuantumResult:
    return QAOASolver().solve(depot, customers, vehicle_config, bypass_clustering)

