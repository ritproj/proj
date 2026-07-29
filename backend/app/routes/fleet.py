"""
GET /api/fleet

Returns demand vs capacity pre-flight check for the current dataset + fleet.
Wraps demand.check_fleet_capacity() — always returns data when a dataset
has been uploaded, regardless of whether solvers have run.
"""
from fastapi import APIRouter, HTTPException, Request
from app.services.demand import check_fleet_capacity

router = APIRouter()


@router.get("/fleet")
async def get_fleet(request: Request):
    customers      = getattr(request.app.state, "customers",      None)
    vehicle_config = getattr(request.app.state, "vehicle_config", None)

    if not customers or not vehicle_config:
        raise HTTPException(
            status_code=400,
            detail="No dataset uploaded. Call POST /api/upload first.",
        )

    return check_fleet_capacity(customers, vehicle_config)
