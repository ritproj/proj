"""
helpers.py — shared utility functions used across the backend.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from app.models.customer import Customer
from app.models.depot import Depot


# ---------------------------------------------------------------------------
# Depot loading
# ---------------------------------------------------------------------------

_DEPOT_JSON_PATH = Path(__file__).parent.parent.parent / "depot.json"


def load_depot() -> Depot:
    """
    Load the depot from depot.json (Option A from spec).
    Raises FileNotFoundError if the file is missing.
    """
    if not _DEPOT_JSON_PATH.exists():
        raise FileNotFoundError(
            f"depot.json not found at {_DEPOT_JSON_PATH}. "
            "Please create it with 'latitude' and 'longitude' fields."
        )
    with open(_DEPOT_JSON_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Depot(
        depot_id=data.get("depot_id", 0),
        latitude=data["latitude"],
        longitude=data["longitude"],
    )


# ---------------------------------------------------------------------------
# Route serialisation → frontend shape
# ---------------------------------------------------------------------------

def routes_to_frontend(
    routes: List[List[int]],
    depot: Depot,
    customers: List[Customer],
    vehicle_types: List[str] = None,
    vehicle_loads: List[float] = None,
    vehicle_caps: List[float] = None,
    dist_matrix=None,
) -> Dict[str, Any]:
    """
    Convert internal routes (node-index lists) to the JSON shape expected
    by the frontend RouteMap component.

    Returns:
      {
        "depot": { "lat": ..., "lng": ... },
        "customers": [ { "id": ..., "lat": ..., "lng": ..., "demand": ... }, ... ],
        "routes": [
          [ { "lat": ..., "lng": ..., "id": null/int, "demand": null/float }, ... ],
          ...
        ],
        "route_meta": [
          { "vehicle": 1, "type": "Van", "stops": 3, "load_kg": 45.0,
            "capacity_kg": 60.0, "load_pct": 75.0, "distance_km": 12.3 },
          ...
        ]
      }
    """
    import numpy as np

    node_data = [{"lat": depot.latitude, "lng": depot.longitude, "id": None, "demand": None}]
    for c in customers:
        node_data.append({
            "lat": c.latitude,
            "lng": c.longitude,
            "id": c.customer_id,
            "demand": c.demand,
        })

    frontend_routes = []
    for route in routes:
        points = [node_data[node] for node in route]
        frontend_routes.append(points)

    # Per-route metadata
    demands_map = {i + 1: c.demand for i, c in enumerate(customers)}
    route_meta = []
    for r_idx, route in enumerate(routes):
        load  = sum(demands_map.get(n, 0) for n in route if n != 0)
        cap   = vehicle_caps[r_idx] if vehicle_caps and r_idx < len(vehicle_caps) else None
        vtype = vehicle_types[r_idx] if vehicle_types and r_idx < len(vehicle_types) else None
        stops = sum(1 for n in route if n != 0)
        km    = None
        if dist_matrix is not None:
            km = round(float(sum(dist_matrix[a][b] for a, b in zip(route, route[1:]))), 3)
        route_meta.append({
            "vehicle":     r_idx + 1,
            "type":        vtype,
            "stops":       stops,
            "load_kg":     round(float(load), 2),
            "capacity_kg": round(float(cap), 2) if cap is not None else None,
            "load_pct":    round(load / cap * 100, 1) if cap else None,
            "distance_km": km,
        })

    return {
        "depot": {"lat": depot.latitude, "lng": depot.longitude},
        "customers": [
            {"id": c.customer_id, "lat": c.latitude, "lng": c.longitude, "demand": c.demand}
            for c in customers
        ],
        "routes":     frontend_routes,
        "route_meta": route_meta,
    }


# ---------------------------------------------------------------------------
# Stats builder
# ---------------------------------------------------------------------------

def build_stats(
    distance_km: float,
    fuel_l: float,
    co2_kg: float,
    n_customers: int,
    n_vehicles: int,
    runtime_s: float,
) -> Dict[str, Any]:
    return {
        "customers":   int(n_customers),
        "vehicles":    int(n_vehicles),
        "distance_km": round(float(distance_km), 2),
        "fuel_l":      round(float(fuel_l), 3),
        "co2_kg":      round(float(co2_kg), 3),
        "runtime_s":   round(float(runtime_s), 4),
    }
