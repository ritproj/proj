"""
POST /api/quantum

Runs the QAOA-based CVRP solver (with feasibility repair / fallback).
Stores the result in app.state.quantum_result.
"""

from fastapi import APIRouter, HTTPException, Request

from app.services.emission import co2_emissions, fuel_consumption
from app.services.qaoa_solver import solve_quantum
from app.utils.helpers import build_stats, routes_to_frontend

router = APIRouter()


@router.post("/quantum")
async def run_quantum(request: Request):
    customers = getattr(request.app.state, "customers", None)
    vehicle_config = getattr(request.app.state, "vehicle_config", None)
    depot = getattr(request.app.state, "depot", None)

    if not customers or not vehicle_config or not depot:
        raise HTTPException(
            status_code=400,
            detail="No dataset uploaded. Call POST /api/upload first.",
        )

    try:
        result = solve_quantum(depot, customers, vehicle_config)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Quantum solver error: {exc}")

    fuel = fuel_consumption(result.total_distance_km, vehicle_config.blended_fuel_rate)
    co2  = co2_emissions(fuel)

    stats = build_stats(
        distance_km=result.total_distance_km,
        fuel_l=fuel,
        co2_kg=co2,
        n_customers=len(customers),
        n_vehicles=len(result.routes),
        runtime_s=result.runtime_s,
    )

    map_data = routes_to_frontend(
        result.routes,
        depot,
        customers,
        vehicle_types=vehicle_config.vehicle_types_list[:len(result.routes)],
        vehicle_caps=vehicle_config.capacities_list[:len(result.routes)],
        dist_matrix=result.distance_matrix,
    )

    response = {
        **map_data,
        "stats": stats,
        "feasible":           result.feasible,
        "fallback_used":      result.fallback_used,
        "objective_best":     result.objective_best,
        "objective_mean":     result.objective_mean,
        "objective_variance": result.objective_variance,
        "runs":               result.runs,
        "n_vars":             result.n_vars,
        "method":             result.method,
    }

    # Persist for comparison + analytics
    request.app.state.quantum_result = {
        "distance_km": result.total_distance_km,
        "fuel_l": fuel,
        "co2_kg": co2,
        "runtime_s": result.runtime_s,
        "feasible": result.feasible,
        "fallback_used": result.fallback_used,
        "objective_best": result.objective_best,
        "objective_mean": result.objective_mean,
        "objective_variance": result.objective_variance,
        "runs": result.runs,
        "n_vars": result.n_vars,
        "method": result.method,
    }
    request.app.state.quantum_routes = result.routes
    if getattr(request.app.state, "dist_matrix", None) is None:
        request.app.state.dist_matrix = result.distance_matrix

    return response
