"""
analytics.py — reshape v1 + v2 outputs into dashboard-ready KPI sections.

No new computation — pure aggregation of data already in app state.
Each section returns None if its prerequisite hasn't run yet (mirrors
v1's /api/compare partial-state pattern, per backend_v2 §17).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from app.models.customer import Customer
from app.models.vehicle import VehicleConfig


def build_analytics(
    customers:         Optional[List[Customer]],
    vehicle_config:    Optional[VehicleConfig],
    classical_state:   Optional[Dict],
    quantum_state:     Optional[Dict],
    classical_routes:  Optional[List[List[int]]],   # node-index routes from classical
    quantum_routes:    Optional[List[List[int]]],   # node-index routes from quantum
    dist_matrix:       Optional[Any],               # np.ndarray or None
    savings:           Optional[Dict],              # from compute_savings()
) -> Dict[str, Any]:
    """
    Build the /api/analytics response.

    Returns a dict with sections: fleet, routing, customers,
    optimization, sustainability.  Any section whose data isn't
    available yet is returned as None.
    """

    # ── Fleet section ─────────────────────────────────────────────────────
    fleet_section = None
    if vehicle_config and (classical_state or quantum_state):
        # Use the result that actually ran — prefer quantum if available
        active_state  = quantum_state or classical_state
        active_routes = quantum_routes or classical_routes or []

        vehicles_used = len(active_routes)
        total_configured = vehicle_config.total_count
        cap_list = vehicle_config.capacities_list

        # Average load utilisation across used routes
        total_demand = sum(c.demand for c in customers) if customers else 0.0
        total_cap_used = sum(cap_list[:vehicles_used]) if cap_list else 0.0
        avg_util = (
            round(total_demand / total_cap_used * 100, 1)
            if total_cap_used > 0 else None
        )

        fleet_section = {
            "vehicles_used":            vehicles_used,
            "total_vehicles_configured": total_configured,
            "average_utilization_pct":  avg_util,
        }

    # ── Routing section ───────────────────────────────────────────────────
    routing_section = None
    active_routes_for_routing = quantum_routes or classical_routes
    active_state_for_routing  = quantum_state  or classical_state

    if active_routes_for_routing and dist_matrix is not None:
        route_lengths = []
        for route in active_routes_for_routing:
            length = sum(float(dist_matrix[a][b]) for a, b in zip(route, route[1:]))
            route_lengths.append(round(length, 3))

        avg_km     = round(float(np.mean(route_lengths)), 3) if route_lengths else 0.0
        longest_km = round(float(max(route_lengths)), 3)     if route_lengths else 0.0
        solver_used = "quantum" if quantum_routes else "classical"

        routing_section = {
            "average_route_km": avg_km,
            "longest_route_km": longest_km,
            "solver_used":      solver_used,
        }

    # ── Customers section ─────────────────────────────────────────────────
    customers_section = None
    if customers and active_routes_for_routing is not None:
        delivered = len(set(
            node
            for route in active_routes_for_routing
            for node in route
            if node != 0
        ))
        customers_section = {
            "delivered": delivered,
            "total":     len(customers),
        }

    # ── Optimization section (QAOA-specific) ─────────────────────────────
    optimization_section = None
    if quantum_state:
        optimization_section = {
            "runtime_s":          quantum_state.get("runtime_s"),
            "runs":               quantum_state.get("runs"),
            "objective_variance": quantum_state.get("objective_variance"),
            "objective_best":     quantum_state.get("objective_best"),
            "objective_mean":     quantum_state.get("objective_mean"),
            "fallback_used":      quantum_state.get("fallback_used"),
        }
    elif classical_state:
        optimization_section = {
            "runtime_s":          classical_state.get("runtime_s"),
            "runs":               1,
            "objective_variance": None,
            "objective_best":     None,
            "objective_mean":     None,
            "fallback_used":      False,
        }

    # ── Sustainability section ────────────────────────────────────────────
    sustainability_section = None
    active_stats = (
        quantum_state if quantum_state
        else classical_state if classical_state
        else None
    )
    if active_stats:
        sustainability_section = {
            "fuel_l":        active_stats.get("fuel_l"),
            "co2_kg":        active_stats.get("co2_kg"),
            "co2_saved_pct": savings.get("co2_pct") if savings else None,
            "fuel_saved_pct": savings.get("fuel_pct") if savings else None,
            "distance_saved_pct": savings.get("distance_pct") if savings else None,
        }

    return {
        "fleet":          fleet_section,
        "routing":        routing_section,
        "customers":      customers_section,
        "optimization":   optimization_section,
        "sustainability": sustainability_section,
    }
