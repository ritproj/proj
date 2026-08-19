"""
GET /api/convergence

Returns the BQPhy per-run QUBO energy history stored after the last
/api/quantum call, so the frontend can display a convergence chart.
"""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/convergence")
async def get_convergence(request: Request):
    qr = getattr(request.app.state, "quantum_result", None)
    if not qr:
        raise HTTPException(
            status_code=400,
            detail="No quantum result available. Run POST /api/quantum first.",
        )

    convergence_data = qr.get("convergence_data") or []
    method = qr.get("method", "unknown")
    runs = qr.get("runs", len(convergence_data))
    objective_best = qr.get("objective_best")
    objective_mean = qr.get("objective_mean")

    return {
        "method": method,
        "runs": runs,
        "convergence_data": convergence_data,
        "objective_best": objective_best,
        "objective_mean": objective_mean,
        "available": len(convergence_data) > 0,
    }
