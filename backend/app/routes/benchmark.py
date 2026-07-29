"""
GET /api/benchmark

Returns classical vs quantum comparison + Decision Engine verdict.
Requires both /api/classical and /api/quantum to have been run first.
"""
from fastapi import APIRouter, HTTPException, Request
from app.services.benchmark import build_benchmark

router = APIRouter()


@router.get("/benchmark")
async def get_benchmark(request: Request):
    classical = getattr(request.app.state, "classical_result", None)
    quantum   = getattr(request.app.state, "quantum_result",   None)

    if not classical and not quantum:
        raise HTTPException(
            status_code=400,
            detail=(
                "No results available. "
                "Run POST /api/classical and POST /api/quantum first."
            ),
        )

    if quantum is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Quantum result not available. "
                "Run POST /api/quantum first to see the Decision Engine verdict."
            ),
        )

    return build_benchmark(classical, quantum)
