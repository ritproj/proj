"""
GET /api/compare

Returns a side-by-side comparison of classical vs quantum results plus
sustainability savings percentages.  Both runs must have been executed first.
"""

from fastapi import APIRouter, HTTPException, Request

from app.services.emission import compute_savings
from app.services.decision_engine import decide

router = APIRouter()


@router.get("/compare")
async def compare_results(request: Request):
    classical = getattr(request.app.state, "classical_result", None)
    quantum   = getattr(request.app.state, "quantum_result",   None)

    if not classical and not quantum:
        raise HTTPException(
            status_code=400,
            detail="No results available. Run classical and/or quantum optimization first.",
        )

    # Build response — allow partial results (only one solver run)
    c = classical or {}
    q = quantum   or {}

    classical_resp = (
        {
            "distance_km": c.get("distance_km"),
            "fuel_l":      c.get("fuel_l"),
            "co2_kg":      c.get("co2_kg"),
            "runtime_s":   c.get("runtime_s"),
        }
        if classical
        else None
    )

    quantum_resp = (
        {
            "distance_km":        q.get("distance_km"),
            "fuel_l":             q.get("fuel_l"),
            "co2_kg":             q.get("co2_kg"),
            "runtime_s":          q.get("runtime_s"),
            "feasible":           q.get("feasible"),
            "fallback_used":      q.get("fallback_used"),
            "objective_best":     q.get("objective_best"),
            "objective_mean":     q.get("objective_mean"),
            "objective_variance": q.get("objective_variance"),
            "runs":               q.get("runs"),
        }
        if quantum
        else None
    )

    # Savings + winner only meaningful when both results present
    savings = None
    winner  = None
    if classical and quantum:
        savings = compute_savings(
            classical_distance=c["distance_km"],
            quantum_distance=q["distance_km"],
            classical_fuel=c["fuel_l"],
            quantum_fuel=q["fuel_l"],
            classical_co2=c["co2_kg"],
            quantum_co2=q["co2_kg"],
        )
        # Use the Decision Engine as the single source of truth for winner —
        # same algorithm as /api/benchmark so both endpoints always agree.
        decision = decide(classical, quantum)
        winner   = decision.winner

    return {
        "classical": classical_resp,
        "quantum":   quantum_resp,
        "savings":   savings,
        "winner":    winner,
    }
