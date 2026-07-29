"""
POST /api/classical

Runs OR-Tools CVRP solver on the currently uploaded dataset.
Stores the result in app.state.classical_result.
"""

from fastapi import APIRouter, HTTPException, Request

from app.services.emission import co2_emissions, fuel_consumption
from app.services.ortools_solver import solve_classical
from app.utils.helpers import build_stats, routes_to_frontend

router = APIRouter()


@router.post("/classical")
async def run_classical(request: Request):
    customers = getattr(request.app.state, "customers", None)
    vehicle_config = getattr(request.app.state, "vehicle_config", None)
    depot = getattr(request.app.state, "depot", None)

    if not customers or not vehicle_config or not depot:
        raise HTTPException(
            status_code=400,
            detail="No dataset uploaded. Call POST /api/upload first.",
        )

    try:
        result = solve_classical(depot, customers, vehicle_config)
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Classical solver error: {exc}")

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
        vehicle_loads=result.vehicle_loads,
        vehicle_caps=result.route_caps,
        dist_matrix=result.distance_matrix,
    )

    response = {
        **map_data,
        "stats": stats,
        "vehicle_loads": result.vehicle_loads,
    }

    # Persist for comparison + analytics
    request.app.state.classical_result = {
        "distance_km": result.total_distance_km,
        "fuel_l": fuel,
        "co2_kg": co2,
        "runtime_s": result.runtime_s,
    }
    request.app.state.classical_routes = result.routes
    request.app.state.dist_matrix = result.distance_matrix

    return response
