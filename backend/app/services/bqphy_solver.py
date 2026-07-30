"""
bqphy_solver.py — BQPhy quantum-inspired backend for GreenRoute V7.

ENCODING (unchanged from qaoa_solver.py)
-----------------------------------------
y[i, k] = 1  if customer i is assigned to vehicle k
Flat index: i * K + k
Total variables: N × K   (e.g. 8 customers × 3 vehicles = 24 binary vars)

QUBO MATRIX (unchanged)
------------------------
Built by build_qubo() — same distance, assignment, and capacity penalties
as before. The matrix Q is identical to what the SA solver used.

SEARCH ALGORITHM (replaced)
----------------------------
Old: exhaustive enumeration (n_vars ≤ 16) + simulated annealing (17–24)
New: BQPhy quantum-inspired evolutionary optimizer (any n_vars)

FITNESS BRIDGE
--------------
BQPhy requires f(x_batch: ndarray[pop, n_vars]) → ndarray[pop].
The QUBO energy x^T Q x is vectorised as:
    np.sum((x_batch @ Q_matrix) * x_batch, axis=1)
This is mathematically identical to evaluate_qubo_energy(x, Q) for each row.
No new formulation. No encoding change.

PIPELINE (unchanged)
---------------------
BQPhy best_vector
    → decode_bitstring()
    → validate_routes()
    → repair_routes()
    → nearest_neighbor_with_2opt() (if repair fails)
    → two_opt_improve()           (if initially valid)
    → QuantumResult
"""
from __future__ import annotations

import logging
import time
from typing import List, Optional

import numpy as np

from app.models.customer import Customer
from app.models.depot import Depot
from app.models.vehicle import VehicleConfig
from app.services.base_solver import BaseQuantumSolver
from app.services.distance import build_distance_matrix
from app.services.quantum_result import QuantumResult
from app.services.qubo import build_qubo
from app.services.repair import (
    decode_bitstring,
    nearest_neighbor_with_2opt,
    repair_routes,
    two_opt_improve,
    validate_routes,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _total_dist(routes: List[List[int]], matrix: np.ndarray) -> float:
    return sum(matrix[a][b] for r in routes for a, b in zip(r, r[1:]))


def _qubo_to_matrix(qubo: dict, n_vars: int) -> np.ndarray:
    Q = np.zeros((n_vars, n_vars), dtype=np.float64)
    for (i, j), val in qubo.items():
        Q[i][j] += val
        if i != j:
            Q[j][i] += val
    return Q


def _soft_decode(
    vec: np.ndarray,
    customers: List[Customer],
    K: int,
    dist_matrix: np.ndarray,
    cap_list: List[float],
) -> List[List[int]]:
    """
    Soft (argmax) decoder: for each customer i, assign to the vehicle k
    with the highest affinity y[i,k] value from the continuous BQPhy output.

    Unlike hard-round decode (which can assign a customer to 0 or 2 vehicles
    when values are near 0.5), argmax guarantees exactly-one assignment.
    Produces feasible assignment structure even when BQPhy hasn't fully converged.
    """
    N = len(customers)
    Y = vec[:N * K].reshape(N, K)   # affinity matrix: Y[i, k]

    # Argmax assignment: each customer goes to its most preferred vehicle
    vehicle_customers: List[List[int]] = [[] for _ in range(K)]
    for i in range(N):
        k_best = int(np.argmax(Y[i]))
        vehicle_customers[k_best].append(i + 1)   # 1-based node index

    # Build nearest-neighbour tour per vehicle (same as decode_bitstring)
    routes: List[List[int]] = []
    for k, assigned in enumerate(vehicle_customers):
        if not assigned:
            routes.append([0, 0])
            continue
        route = [0]
        unvisited = list(assigned)
        current = 0
        while unvisited:
            nearest = min(unvisited, key=lambda j: dist_matrix[current][j])
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        route.append(0)
        routes.append(route)

    return routes


def _or_opt_improve(
    routes: List[List[int]],
    dist_matrix: np.ndarray,
    customers: List[Customer],
    capacities: List[float],
) -> List[List[int]]:
    """
    Or-opt: try moving each single customer from its current route to a
    better position in any other route. Only accept moves that:
      - Reduce total distance, AND
      - Don't violate the destination vehicle's capacity.

    This is an inter-route improvement that 2-opt (intra-route only) cannot do.
    Runs a single pass over all (customer, destination_route) pairs.
    """
    demands = {c.customer_id: c.demand for c in customers}
    n = len(routes)
    improved = True

    while improved:
        improved = False
        for src in range(n):
            if len(routes[src]) <= 3:   # only depot + 1 customer + depot — can't remove
                continue
            for pos in range(1, len(routes[src]) - 1):   # each customer in src
                node = routes[src][pos]
                d_node = demands.get(node, 0)

                # Cost of removing node from src
                prev_s = routes[src][pos - 1]
                next_s = routes[src][pos + 1]
                removal_gain = (
                    dist_matrix[prev_s][node]
                    + dist_matrix[node][next_s]
                    - dist_matrix[prev_s][next_s]
                )

                for dst in range(n):
                    if dst == src:
                        continue
                    # Check dst capacity
                    dst_load = sum(demands.get(x, 0) for x in routes[dst] if x != 0)
                    dst_cap  = capacities[dst] if dst < len(capacities) else capacities[-1]
                    if dst_load + d_node > dst_cap + 1e-6:
                        continue

                    # Try each insertion position in dst
                    for ins in range(1, len(routes[dst])):
                        prev_d = routes[dst][ins - 1]
                        next_d = routes[dst][ins]
                        insertion_cost = (
                            dist_matrix[prev_d][node]
                            + dist_matrix[node][next_d]
                            - dist_matrix[prev_d][next_d]
                        )
                        net_gain = removal_gain - insertion_cost
                        if net_gain > 1e-9:    # improvement found
                            # Apply move
                            routes[src].pop(pos)
                            routes[dst].insert(ins, node)
                            improved = True
                            break
                    if improved:
                        break
                if improved:
                    break
            if improved:
                break

    return routes


def _nn_result(
    dist_matrix: np.ndarray,
    customers: List[Customer],
    K: int,
    cap_list: List[float],
) -> QuantumResult:
    """NN+2opt fallback result — used when BQPhy is unavailable or fails."""
    t0 = time.perf_counter()
    routes = nearest_neighbor_with_2opt(dist_matrix, customers, K, cap_list)
    rt = time.perf_counter() - t0
    km = _total_dist(routes, dist_matrix)
    feasible, _ = validate_routes(routes, customers, cap_list)
    reason = None if feasible else "ROUTE_VALIDATION_FAILED"
    return QuantumResult(
        routes=routes,
        total_distance_km=round(float(km), 3),
        runtime_s=round(rt, 4),
        feasible=feasible,
        fallback_used=True,
        objective_best=round(float(km), 4),
        objective_mean=round(float(km), 4),
        objective_variance=0.0,
        runs=0,
        n_vars=0,
        method="nn_fallback",
        distance_matrix=dist_matrix,
        infeasible_reason=reason,
    )


# ---------------------------------------------------------------------------
# Core BQPhy solve
# ---------------------------------------------------------------------------

def _bqphy_solve_direct(
    depot: Depot,
    customers: List[Customer],
    vehicle_config: VehicleConfig,
) -> QuantumResult:
    """
    Run BQPhy on the existing N×K QUBO encoding.
    The fitness function is the vectorised QUBO energy — no arc-flow, no new formulation.
    """
    import bqphy.BQPhy_Optimiser as qea  # deferred: ImportError handled by caller
    from app import config

    dist_matrix = build_distance_matrix(depot, customers)
    K = vehicle_config.total_count
    cap_list = vehicle_config.capacities_list
    N = len(customers)

    # Clamp K so n_vars ≤ BQPHY_QUBIT_LIMIT (BQPhy handles larger vars than SA,
    # so the default ceiling is much higher).
    qubit_limit = getattr(config, "BQPHY_QUBIT_LIMIT", 128)
    K_eff = min(K, qubit_limit // N) if N > 0 else K
    K_eff = max(K_eff, 1)
    n_vars = N * K_eff

    print(f"\n[BQPhy] Starting BQPhy Optimization...")
    print(f"[BQPhy] Problem: {N} customers | {K_eff} effective vehicles | "
          f"{n_vars} binary variables (y[i,k] encoding)")
    logger.info(f"[BQPhy] {N} customers, {K_eff} vehicles, {n_vars} vars")

    # ── Build QUBO (exactly as qaoa_solver does) ────────────────────────────
    qubo_dict, _, _ = build_qubo(
        distance_matrix=dist_matrix,
        customers=customers,
        n_vehicles=K_eff,
        capacities=cap_list[:K_eff],
    )
    Q_matrix = _qubo_to_matrix(qubo_dict, n_vars)

    # ── Vectorised QUBO fitness bridge ──────────────────────────────────────
    # x_batch shape: (numPopulation, n_vars)
    # QUBO energy per candidate: x_i^T Q x_i = sum((x_batch @ Q) * x_batch, axis=1)
    # Mathematically identical to evaluate_qubo_energy(x, Q) applied row-wise.
    def qubo_fitness(x_batch: np.ndarray) -> np.ndarray:
        return np.sum((x_batch @ Q_matrix) * x_batch, axis=1)

    # ── BQPhy configuration — adaptive scaling based on problem size ───────────
    # Base values from config
    base_pop  = getattr(config, "BQPHY_POPULATION",  200)
    base_gen  = getattr(config, "BQPHY_GENERATIONS", 800)
    delta_theta = getattr(config, "BQPHY_DELTA_THETA", 0.12)
    base_runs   = getattr(config, "BQPHY_RUNS", 3)

    # Scale population and generations with problem size:
    #   n_vars ≤ 30  : small   — base values, more restarts (5)
    #   n_vars ≤ 100 : medium  — 1.5× population, 1.25× generations
    #   n_vars ≤ 250 : large   — 2×  population, 1.5×  generations
    #   n_vars >  250: xl      — 3×  population, 2×    generations
    # deltaTheta decreases for larger problems: smaller rotation = finer
    # exploration = more likely to escape infeasible local minima.
    if n_vars <= 30:
        population  = base_pop
        generations = base_gen
        n_runs      = min(base_runs + 2, 5)   # up to 5 restarts — fast anyway
        dt          = delta_theta              # 0.12 — standard
    elif n_vars <= 100:
        population  = int(base_pop * 1.5)
        generations = int(base_gen * 1.25)
        n_runs      = base_runs                # 3 restarts
        dt          = delta_theta * 0.8        # 0.096 — slightly finer
    elif n_vars <= 250:
        population  = int(base_pop * 2)
        generations = int(base_gen * 1.5)
        n_runs      = max(base_runs - 1, 1)   # 2 restarts
        dt          = delta_theta * 0.6        # 0.072 — finer exploration
    else:
        population  = int(base_pop * 3)
        generations = int(base_gen * 2)
        n_runs      = 1                        # single run — each is thorough
        dt          = delta_theta * 0.5        # 0.06 — finest exploration

    optimizer_cfg = {
        "numPopulation":            population,
        "maxGeneration":            generations,
        "deltaTheta":               dt,
        "designVariables":          n_vars,
        "typeOfOptimisation":       "BINARY",
        "populationInitialSeeding": False,
        "outputFilePath":           "bqphy_solver_output",
        "generationLogging":        getattr(config, "BQPHY_GEN_LOGGING", "noLogging"),
    }

    print(f"[BQPhy] Adaptive config: population={population}, generations={generations}, "
          f"deltaTheta={dt:.4f}, runs={n_runs}  [n_vars={n_vars}]")
    print(f"[BQPhy] Running quantum-inspired evolutionary optimization...")


    t0 = time.perf_counter()

    best_vector:  Optional[np.ndarray] = None
    best_fitness: float = float("inf")
    all_fitnesses: List[float] = []

    for run_idx in range(n_runs):
        optimizer = qea.BQPhy_OPTIMISER()
        optimizer.initialize(optimizer_cfg)
        optimizer.model(qubo_fitness)
        optimizer.runOptimization()
        vec, fit = optimizer.getBestDesign()
        fit = float(np.asarray(fit).flat[0])
        vec = np.asarray(vec, dtype=np.float64).ravel()
        all_fitnesses.append(fit)
        print(f"[BQPhy] Run {run_idx + 1}/{n_runs} — QUBO energy: {fit:.4f}")
        if fit < best_fitness:
            best_fitness = fit
            best_vector  = vec

    rt = time.perf_counter() - t0
    obj_mean = float(np.mean(all_fitnesses))
    obj_var  = float(np.var(all_fitnesses))

    print(f"[BQPhy] Optimization complete — best of {n_runs} runs.")
    
    # ── Decode best binary vector — try multiple strategies ─────────────────
    # Strategy 1: Hard-round (y > 0.5 → 1). Standard approach.
    # Strategy 2: Soft argmax (each customer → vehicle with highest affinity).
    #             Guarantees exactly-one assignment even when BQPhy partially converges.
    # We try both and keep the first that is feasible after repair.

    candidate_routes = []

    # Hard-round decode
    bitstring = "".join(str(int(round(b))) for b in best_vector)
    hard_routes = decode_bitstring(bitstring, customers, K_eff, dist_matrix, cap_list[:K_eff])
    candidate_routes.append(("hard", hard_routes))

    # Soft argmax decode
    soft_routes = _soft_decode(best_vector, customers, K_eff, dist_matrix, cap_list[:K_eff])
    candidate_routes.append(("soft", soft_routes))

    print(f"[BQPhy] Decoding {len(bitstring)}-bit solution — trying hard + soft decode...")

    routes        = None
    fallback_used = False
    route_source  = "none"

    for strategy_name, candidate in candidate_routes:
        feasible, _ = validate_routes(candidate, customers, cap_list[:K_eff])
        if not feasible:
            repaired, feasible = repair_routes(candidate, customers, cap_list[:K_eff], dist_matrix)
            candidate = repaired
        if feasible:
            routes = two_opt_improve(candidate, dist_matrix)
            route_source = strategy_name
            print(f"[BQPhy] Decode '{strategy_name}' produced feasible routes.")
            break

    if routes is None:
        # Both strategies failed — NN+2opt fallback
        print("[BQPhy] Both decoders failed — nearest_neighbor_with_2opt() fallback...")
        routes = nearest_neighbor_with_2opt(dist_matrix, customers, K, cap_list)
        feasible, _ = validate_routes(routes, customers, cap_list)
        fallback_used = True
        route_source  = "nn_fallback"

    print(f"[BQPhy] Route source: {route_source}  |  fallback_used={fallback_used}")

    # ── Or-opt inter-route improvement (if not fallback) ────────────────────
    # Or-opt moves single customers between routes to reduce total distance.
    # Only applied to BQPhy-decoded routes (not NN fallback — already optimized).
    if not fallback_used:
        routes = _or_opt_improve(routes, dist_matrix, customers, cap_list)
        routes = two_opt_improve(routes, dist_matrix)  # final 2-opt pass

    # ── Final safety check ──────────────────────────────────────────────────
    final_feasible, _ = validate_routes(routes, customers, cap_list)
    if not final_feasible:
        feasible = False

    print(f"[BQPhy] Final route loads:")
    demands_map = {c.customer_id: c.demand for c in customers}
    for i, r in enumerate(routes):
        load = sum(demands_map.get(n, 0) for n in r if n != 0)
        print(f"         Vehicle {i+1}: {load:.1f} kg")
    print(f"[BQPhy] fallback_used={fallback_used}")

    total_km = _total_dist(routes, dist_matrix)
    reason = None if feasible else "CAPACITY_VIOLATION_AFTER_REPAIR"

    return QuantumResult(
        routes=routes,
        total_distance_km=round(float(total_km), 3),
        runtime_s=round(rt, 4),
        feasible=feasible,
        fallback_used=fallback_used,
        objective_best=round(best_fitness, 4),
        objective_mean=round(obj_mean, 4),
        objective_variance=round(obj_var, 4),
        runs=n_runs,
        n_vars=n_vars,
        method="bqphy",
        distance_matrix=dist_matrix,
        infeasible_reason=reason,
    )


# ---------------------------------------------------------------------------
# BQPhySolver — implements BaseQuantumSolver
# ---------------------------------------------------------------------------

class BQPhySolver(BaseQuantumSolver):
    """
    Quantum-inspired CVRP solver using BQPhy as the search engine.

    Encoding  : y[i,k] ∈ {0,1}, N×K binary variables — identical to QAOASolver.
    Formulation: QUBO matrix built by build_qubo()       — identical to QAOASolver.
    Search    : BQPhy QIEO optimizer                     — replaces SA/exhaustive.
    Pipeline  : decode → validate → repair → NN+2opt     — identical to QAOASolver.

    If bqphy is not installed, degrades gracefully to nearest-neighbour fallback
    and logs a clear installation instruction.
    """

    def solve(
        self,
        depot: Depot,
        customers: List[Customer],
        vehicle_config: VehicleConfig,
        bypass_clustering: bool = False,
    ) -> QuantumResult:
        from app import config

        dist_matrix = build_distance_matrix(depot, customers)
        K = vehicle_config.total_count
        cap_list = vehicle_config.capacities_list

        # ── Upfront feasibility guard (verbatim from qaoa_solver) ──────────
        total_demand = sum(c.demand for c in customers)
        total_cap    = sum(cap_list)
        max_demand   = max((c.demand for c in customers), default=0)
        max_cap      = max(cap_list, default=0)

        if total_demand > total_cap + 1e-6:
            return QuantumResult(
                routes=[], total_distance_km=0.0, runtime_s=0.0,
                feasible=False, fallback_used=False,
                objective_best=0.0, objective_mean=0.0, objective_variance=0.0,
                runs=0, n_vars=0, method="infeasible", distance_matrix=dist_matrix,
                infeasible_reason="TOTAL_DEMAND_EXCEEDS_FLEET_CAPACITY",
            )
        if max_demand > max_cap + 1e-6:
            return QuantumResult(
                routes=[], total_distance_km=0.0, runtime_s=0.0,
                feasible=False, fallback_used=False,
                objective_best=0.0, objective_mean=0.0, objective_variance=0.0,
                runs=0, n_vars=0, method="infeasible", distance_matrix=dist_matrix,
                infeasible_reason="CUSTOMER_EXCEEDS_MAX_VEHICLE_CAPACITY",
            )

        # ── Cluster large instances (BQPhy limit >> SA limit) ───────────────
        bqphy_limit = getattr(config, "BQPHY_CUSTOMER_LIMIT", 16)
        if len(customers) > bqphy_limit and not bypass_clustering:
            logger.info(
                f"[BQPhy] {len(customers)} customers exceeds BQPHY_CUSTOMER_LIMIT "
                f"({bqphy_limit}). Using clustered path."
            )
            from app.services.qaoa_solver import _solve_clustered_quantum
            return _solve_clustered_quantum(depot, customers, vehicle_config)

        # ── Run BQPhy; degrade gracefully on ImportError ────────────────────
        try:
            return _bqphy_solve_direct(depot, customers, vehicle_config)
        except ImportError:
            logger.error(
                "[BQPhy] bqphy package not installed.\n"
                "  To activate: switch to Python 3.12 and run:\n"
                "  pip install D:\\quantum\\experiment\\Hackathon_Package\\"
                "bqphy-26.5.0-cp312-cp312-win_amd64.whl\n"
                "  Falling back to nearest-neighbour."
            )
            print(
                "[BQPhy] ERROR: bqphy not installed. "
                "Returning nearest-neighbour fallback."
            )
            return _nn_result(dist_matrix, customers, K, cap_list)
        except Exception as exc:
            logger.error(f"[BQPhy] Unexpected error: {exc}")
            print(f"[BQPhy] ERROR: {exc}. Returning nearest-neighbour fallback.")
            return _nn_result(dist_matrix, customers, K, cap_list)
