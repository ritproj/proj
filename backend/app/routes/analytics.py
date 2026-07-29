"""
GET /api/analytics

Returns fleet / routing / customers / optimization / sustainability KPIs.
Each section is null when its prerequisite hasn't run yet — same partial-state
pattern as v1's /api/compare.
"""
from fastapi import APIRouter, HTTPException, Request
from app.services.analytics import build_analytics
from app.services.emission import compute_savings

router = APIRouter()


@router.get("/analytics")
async def get_analytics(request: Request):
    customers      = getattr(request.app.state, "customers",         None)
    vehicle_config = getattr(request.app.state, "vehicle_config",    None)
    classical      = getattr(request.app.state, "classical_result",  None)
    quantum        = getattr(request.app.state, "quantum_result",    None)
    classical_routes = getattr(request.app.state, "classical_routes", None)
    quantum_routes   = getattr(request.app.state, "quantum_routes",   None)
    dist_matrix    = getattr(request.app.state, "dist_matrix",       None)

    if not customers:
        raise HTTPException(
            status_code=400,
            detail="No dataset uploaded. Call POST /api/upload first.",
        )

    # Compute savings if both solvers have run
    savings = None
    if classical and quantum:
        savings = compute_savings(
            classical["distance_km"], quantum["distance_km"],
            classical["fuel_l"],      quantum["fuel_l"],
            classical["co2_kg"],      quantum["co2_kg"],
        )

    return build_analytics(
        customers=customers,
        vehicle_config=vehicle_config,
        classical_state=classical,
        quantum_state=quantum,
        classical_routes=classical_routes,
        quantum_routes=quantum_routes,
        dist_matrix=dist_matrix,
        savings=savings,
    )
