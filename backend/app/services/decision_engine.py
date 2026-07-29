"""
decision_engine.py — score two feasible CVRP results and pick a winner.

Scoring model (ADR-003, backend_v2 Part 2 §14)
----------------------------------------------
Two independent signals only:
  • Distance  — the quantity the solvers actually optimise
  • Runtime   — the real cost tradeoff worth surfacing

Both are min-max normalised to [0, 1] (1 = better, i.e. lower raw value)
before weighting.  Fuel and CO₂ are excluded from the *decision score*
specifically because they are exact linear functions of distance under the
current blended-rate fleet model — counting them here would be triple-counting
the same signal.  They remain fully reported in /compare, /benchmark, and the
dashboard sustainability section.

Weights are read from config.py so Day-1 tuning doesn't require touching this
file.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.config import DECISION_DISTANCE_WEIGHT, DECISION_RUNTIME_WEIGHT


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class DecisionResult:
    winner:            str            # "classical" | "quantum"
    reason:            str            # one-sentence, judge-readable explanation
    classical_score:   float          # normalised composite, in [0, 1]
    quantum_score:     float          # normalised composite, in [0, 1]
    scoring_breakdown: Dict[str, Any] # per-metric normalised contributions


# ---------------------------------------------------------------------------
# Normalisation helper
# ---------------------------------------------------------------------------

def _normalize(classical_val: float, quantum_val: float):
    """
    Min-max normalise a pair of values so that 1.0 = better (lower raw = higher score).

    Returns (classical_norm, quantum_norm), both in [0, 1].
    Ties produce (1.0, 1.0) — both score full marks on that metric.
    """
    lo = min(classical_val, quantum_val)
    hi = max(classical_val, quantum_val)
    if hi == lo:
        return 1.0, 1.0
    span = hi - lo
    return (
        1.0 - (classical_val - lo) / span,
        1.0 - (quantum_val   - lo) / span,
    )


def _score(distance_norm: float, runtime_norm: float) -> float:
    return DECISION_DISTANCE_WEIGHT * distance_norm + DECISION_RUNTIME_WEIGHT * runtime_norm


# ---------------------------------------------------------------------------
# Reason builder
# ---------------------------------------------------------------------------

def _explain(
    classical: Dict,
    quantum:   Dict,
    winner:    str,
    q_dist_n:  float,
    q_rt_n:    float,
) -> str:
    c_dist = classical["distance_km"]
    q_dist = quantum["distance_km"]
    c_rt   = classical["runtime_s"]
    q_rt   = quantum["runtime_s"]

    fallback_note = " (fallback heuristic was used)" if quantum.get("fallback_used") else ""

    if winner == "quantum":
        dist_delta = round((c_dist - q_dist) / c_dist * 100, 1) if c_dist else 0
        if q_rt > c_rt:
            return (
                f"Quantum route is {dist_delta}% shorter{fallback_note}; "
                f"the extra {round(q_rt - c_rt, 2)}s simulator runtime is accepted "
                f"given the distance improvement."
            )
        else:
            return (
                f"Quantum route is {dist_delta}% shorter and also faster{fallback_note}; "
                f"it wins on both primary metrics."
            )
    else:
        if q_dist <= c_dist:
            # runtime decided it
            return (
                f"Classical route matches or improves on quantum distance "
                f"and completes in {round(c_rt, 2)}s vs quantum's {round(q_rt, 2)}s."
            )
        dist_delta = round((q_dist - c_dist) / c_dist * 100, 1) if c_dist else 0
        return (
            f"Classical route is {dist_delta}% shorter than quantum{fallback_note}; "
            f"OR-Tools found a better solution on this instance."
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def decide(
    classical: Dict,
    quantum:   Dict,
) -> DecisionResult:
    """
    Score two feasible CVRP results and return a DecisionResult.

    Parameters
    ----------
    classical : dict with keys distance_km, runtime_s
    quantum   : dict with keys distance_km, runtime_s, feasible, fallback_used

    Repair/fallback must have already run on the quantum result before this
    function is called (ADR-004, backend_v2 §8 step 9).
    """
    # --- Infeasibility short-circuit ---
    if not quantum.get("feasible", False):
        return DecisionResult(
            winner="classical",
            reason="Quantum route infeasible even after repair/fallback — classical wins by default.",
            classical_score=1.0,
            quantum_score=0.0,
            scoring_breakdown={"distance": None, "runtime": None,
                               "note": "quantum infeasible, no normalization performed"},
        )

    # --- Missing classical data guard ---
    if not classical or classical.get("distance_km") is None:
        return DecisionResult(
            winner="quantum",
            reason="Classical result not available — quantum result used by default.",
            classical_score=0.0,
            quantum_score=1.0,
            scoring_breakdown={"distance": None, "runtime": None,
                               "note": "classical result missing"},
        )

    # --- Normalise and score ---
    c_dist_n, q_dist_n = _normalize(classical["distance_km"], quantum["distance_km"])
    c_rt_n,   q_rt_n   = _normalize(classical["runtime_s"],   quantum["runtime_s"])

    c_score = _score(c_dist_n, c_rt_n)
    q_score = _score(q_dist_n, q_rt_n)

    winner = "quantum" if q_score > c_score else "classical"
    reason = _explain(classical, quantum, winner, q_dist_n, q_rt_n)

    return DecisionResult(
        winner=winner,
        reason=reason,
        classical_score=round(c_score, 3),
        quantum_score=round(q_score, 3),
        scoring_breakdown={
            "distance":       round(q_dist_n, 3),
            "runtime":        round(q_rt_n,   3),
            "fuel_co2_note":  (
                "excluded from score — linear in distance under current "
                "blended-rate fleet model, not an independent signal"
            ),
        },
    )
