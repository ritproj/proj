"""
ortools_solver.py — Capacitated VRP solved with Google OR-Tools.

Each vehicle has its own capacity from vehicle_config.capacities_list.
Returns a ClassicalResult object containing routes, distance, and metrics.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List

import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from app.models.customer import Customer
from app.models.depot import Depot
from app.models.vehicle import VehicleConfig
from app.services.distance import build_distance_matrix, matrix_to_int


@dataclass
class ClassicalResult:
    routes: List[List[int]]
    total_distance_km: float
    vehicle_loads: List[float]
    route_caps: List[float]            # capacity for each non-empty route
    runtime_s: float
    distance_matrix: np.ndarray = field(repr=False)


def solve_classical(
    depot: Depot,
    customers: List[Customer],
    vehicle_config: VehicleConfig,
) -> ClassicalResult:
    """
    Solve CVRP with OR-Tools.  Each vehicle slot gets its own capacity
    from vehicle_config.capacities_list.
    """
    t0 = time.perf_counter()

    dist_matrix_km  = build_distance_matrix(depot, customers)
    dist_matrix_int = matrix_to_int(dist_matrix_km)
    n_nodes         = len(dist_matrix_int)

    K          = vehicle_config.total_count
    cap_list   = vehicle_config.capacities_list        # length K, per-slot
    demands    = [0] + [round(c.demand) for c in customers]

    manager = pywrapcp.RoutingIndexManager(n_nodes, K, 0)
    routing = pywrapcp.RoutingModel(manager)

    # Distance callback
    def distance_cb(from_idx: int, to_idx: int) -> int:
        return dist_matrix_int[manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)]

    transit_idx = routing.RegisterTransitCallback(distance_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    # Demand callback
    def demand_cb(from_idx: int) -> int:
        return demands[manager.IndexToNode(from_idx)]

    demand_idx = routing.RegisterUnaryTransitCallback(demand_cb)
    routing.AddDimensionWithVehicleCapacity(
        demand_idx,
        0,
        [int(c) for c in cap_list],
        True,
        "Capacity",
    )

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    params.time_limit.seconds = 2  # reduced so quantum (SA-QUBO) can compete on demo datasets

    solution = routing.SolveWithParameters(params)
    runtime_s = time.perf_counter() - t0

    if not solution:
        raise RuntimeError(
            "OR-Tools could not find a feasible solution. "
            "Check vehicle counts / capacities vs total demand."
        )

    routes: List[List[int]] = []
    vehicle_loads: List[float] = []
    route_caps: List[float] = []        # capacity for each non-empty route

    for vid in range(K):
        idx   = routing.Start(vid)
        route = []
        load  = 0.0
        while not routing.IsEnd(idx):
            node = manager.IndexToNode(idx)
            route.append(node)
            load += demands[node]
            idx = solution.Value(routing.NextVar(idx))
        route.append(0)
        routes.append(route)
        vehicle_loads.append(load)
        route_caps.append(cap_list[vid])

    total_km = _routes_total_distance(routes, dist_matrix_km)

    return ClassicalResult(
        routes=routes,
        total_distance_km=round(float(total_km), 3),
        vehicle_loads=vehicle_loads,
        route_caps=route_caps,
        runtime_s=round(runtime_s, 4),
        distance_matrix=dist_matrix_km,
    )


def _routes_total_distance(routes: List[List[int]], matrix: np.ndarray) -> float:
    return sum(matrix[a][b] for route in routes for a, b in zip(route, route[1:]))
