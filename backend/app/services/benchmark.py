"""
benchmark.py — package classical + quantum stats + Decision Engine result
               into the /api/benchmark response shape.

All numbers come from app state (already computed by v1 routes).
No new computation here — just reshaping + calling decision_engine.decide().
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.services.decision_engine import DecisionResult, decide


@dataclass
class BenchmarkResult:
    classical: Dict[str, Any]
    quantum:   Dict[str, Any]
    winner:    str
    decision:  DecisionResult


def build_benchmark(
    classical_state: Optional[Dict],
    quantum_state:   Optional[Dict],
) -> Dict[str, Any]:
    """
    Build the /api/benchmark response.

    Parameters
    ----------
    classical_state : app.state.classical_result  (may be None if not run yet)
    quantum_state   : app.state.quantum_result    (may be None if not run yet)

    Returns the full benchmark dict including the Decision Engine verdict.
    Returns partial data (null sections) for whichever solver hasn't run yet,
    mirroring v1's /api/compare partial-state pattern.
    """
    classical_resp = (
        {
            "distance_km": classical_state.get("distance_km"),
            "fuel_l":      classical_state.get("fuel_l"),
            "co2_kg":      classical_state.get("co2_kg"),
            "runtime_s":   classical_state.get("runtime_s"),
            "feasible":    True,  # OR-Tools always returns a feasible result or raises
        }
        if classical_state else None
    )

    quantum_resp = (
        {
            "distance_km":        quantum_state.get("distance_km"),
            "fuel_l":             quantum_state.get("fuel_l"),
            "co2_kg":             quantum_state.get("co2_kg"),
            "runtime_s":          quantum_state.get("runtime_s"),
            "feasible":           quantum_state.get("feasible"),
            "fallback_used":      quantum_state.get("fallback_used"),
            "objective_best":     quantum_state.get("objective_best"),
            "objective_mean":     quantum_state.get("objective_mean"),
            "objective_variance": quantum_state.get("objective_variance"),
            "runs":               quantum_state.get("runs"),
            "n_vars":             quantum_state.get("n_vars"),
            "method":             quantum_state.get("method"),
        }
        if quantum_state else None
    )

    # Decision Engine runs only when both results are available
    if classical_state and quantum_state:
        decision = decide(classical_state, quantum_state)
        winner   = decision.winner
        decision_resp = {
            "reason":            decision.reason,
            "classical_score":   decision.classical_score,
            "quantum_score":     decision.quantum_score,
            "scoring_breakdown": decision.scoring_breakdown,
        }
    else:
        winner        = None
        decision_resp = None

    return {
        "classical": classical_resp,
        "quantum":   quantum_resp,
        "winner":    winner,
        "decision":  decision_resp,
    }
