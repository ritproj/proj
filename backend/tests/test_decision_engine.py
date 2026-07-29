import pytest
from app.services.decision_engine import decide, DecisionResult

def test_decide_quantum_infeasible():
    # Quantum is infeasible: classical must win by default
    classical = {"distance_km": 10.0, "runtime_s": 0.1}
    quantum = {"distance_km": 8.0, "runtime_s": 5.0, "feasible": False, "fallback_used": False}
    res = decide(classical, quantum)
    assert res.winner == "classical"
    assert "infeasible" in res.reason.lower()
    assert res.classical_score == 1.0
    assert res.quantum_score == 0.0

def test_decide_classical_missing():
    # Classical is missing: quantum must win by default
    classical = None
    quantum = {"distance_km": 8.0, "runtime_s": 5.0, "feasible": True, "fallback_used": False}
    res = decide(classical, quantum)
    assert res.winner == "quantum"
    assert "not available" in res.reason.lower()
    assert res.classical_score == 0.0
    assert res.quantum_score == 1.0

def test_decide_tie_and_scores():
    # Distances and runtimes are equal: tie in score but classical wins (as tie-breaker or fallback)
    classical = {"distance_km": 10.0, "runtime_s": 1.0}
    quantum = {"distance_km": 10.0, "runtime_s": 1.0, "feasible": True, "fallback_used": False}
    res = decide(classical, quantum)
    # Tie means both normalize to 1.0 on all metrics, so score is 1.0 for both.
    assert res.classical_score == 1.0
    assert res.quantum_score == 1.0
    assert res.winner == "classical" # due to <= in decide() logic
    assert "matches or improves" in res.reason.lower()

def test_decide_quantum_wins():
    # Quantum has shorter distance and is faster (both normalized to 1.0 vs 0.0)
    classical = {"distance_km": 12.0, "runtime_s": 2.0}
    quantum = {"distance_km": 10.0, "runtime_s": 1.0, "feasible": True, "fallback_used": False}
    res = decide(classical, quantum)
    assert res.winner == "quantum"
    assert res.quantum_score > res.classical_score
    assert "shorter and also faster" in res.reason.lower()
