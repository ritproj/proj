"""
POST /api/reset

Clears all in-memory solver state so the user can start fresh
without uploading a new dataset. The dataset + vehicle config
are preserved; only solver results are wiped.

Use DELETE /api/reset to also wipe the dataset (full reset).
"""
from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/reset")
async def reset_results(request: Request):
    """Clear solver results only (dataset kept)."""
    request.app.state.classical_result  = None
    request.app.state.quantum_result    = None
    request.app.state.classical_routes  = None
    request.app.state.quantum_routes    = None
    request.app.state.dist_matrix       = None
    return {"message": "Solver results cleared. Dataset and fleet config preserved."}


@router.delete("/reset")
async def full_reset(request: Request):
    """Full reset — clears everything including dataset."""
    request.app.state.customers         = None
    request.app.state.vehicle_config    = None
    request.app.state.depot             = None
    request.app.state.classical_result  = None
    request.app.state.quantum_result    = None
    request.app.state.classical_routes  = None
    request.app.state.quantum_routes    = None
    request.app.state.dist_matrix       = None
    return {"message": "Full reset complete. Upload a new dataset to continue."}
