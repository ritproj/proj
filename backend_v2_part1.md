
# backend_v2.md — Part 1
## GreenRoute Backend Architecture V2

> **Version:** 2.1 (revised — aligned with the working v1 implementation)
> **Purpose:** Scale the existing backend (`backend_v1.md` / the built prototype) into a
> judge-facing, production-style architecture for the Quant-A-thon 36-hour final,
> **without breaking or contradicting what v1 already does correctly.**

---

# 0. Non-Negotiable Constraint (NEW)

Everything in this document is *additive*. The following v1 behavior is locked and
must keep working exactly as-is, verified by running the existing test suite before
and after every change:

```
POST /api/upload
POST /api/classical
POST /api/quantum
GET  /api/compare
```

- The assignment-variable QUBO encoding (`y[i,k]`, see §11) is the encoding used —
  it is not being replaced.
- The QAOA customer/qubit limits already proven in v1 are the real limits — nothing
  in v2 raises them without new evidence.
- Repair/fallback logic order is not changed, only extended (see §8).

If a v2 change would require breaking any of the above, that change is out of scope
for this hackathon and goes in §21 (Future Scope) instead.

---

# 1. Design Philosophy

This document **extends** the existing backend. Nothing from v1 is discarded or
re-implemented from scratch. V2's job is to wrap v1's working optimization core with:

- a decision layer that picks a winner honestly,
- a benchmarking layer that makes the comparison legible to judges,
- an analytics layer that turns raw numbers into a dashboard story.

Current (v1) pipeline — unchanged:

```text
Upload
 ↓
Validation
 ↓
Distance Matrix
 ↓
OR-Tools
 ↓
QUBO (assignment-variable, y[i,k])
 ↓
QAOA
 ↓
Repair / Fallback
 ↓
Emission
 ↓
Comparison
```

New (v2) pipeline — wraps the above, does not reorder its internals:

```text
Upload
 ↓
Validation
 ↓
Demand Analysis            (NEW — lightweight, informational)
 ↓
Distance Matrix
 ↓
Customer Clustering        (NEW — only when N > QAOA_CUSTOMER_LIMIT, same
                             trigger v1 already uses for its clustering notice)
 ↓
OR-Tools  ──────┐
                ├── (run independently, both feed Decision Engine)
QUBO → QAOA ────┘
 ↓
Repair / Fallback           (unchanged from v1 — runs on the QAOA result
                             BEFORE it reaches the Decision Engine)
 ↓
Decision Engine             (NEW — scores only feasible routes)
 ↓
Benchmark                   (NEW — records the multi-run stats v1 already computes)
 ↓
Sustainability / Emission   (existing v1 logic, reused)
 ↓
Analytics                   (NEW — reshapes the above for the dashboard)
 ↓
Frontend APIs
```

The key correction from the previous draft: **Repair happens before the Decision
Engine sees the quantum result**, never after. Scoring an unrepaired, possibly
infeasible QAOA bitstring against OR-Tools' always-feasible output would not be a
fair comparison and would silently corrupt the benchmark numbers.

---

# 2. Objectives

## Existing Objectives (v1, unchanged)
- Read customer dataset
- Solve CVRP with OR-Tools
- Solve CVRP with QAOA (assignment-variable QUBO, on a bounded instance size)
- Repair/fallback infeasible QAOA output
- Compare OR-Tools and QAOA
- Calculate fuel and CO₂

## New Objectives (v2, scoped to what's achievable in 36 hours)
1. **Decision Engine** — pick and explain a winner (highest judge-visibility item)
2. **Benchmark endpoint** — expose the multi-run stats v1 already computes, structured for a dashboard
3. **Analytics endpoint** — reshape existing numbers into fleet/routing/sustainability KPIs
4. **Demand analysis** — a cheap pre-flight check (total demand vs. total fleet capacity)
5. **Clustering integration** — wire v1's existing k-means clustering into the live pipeline for oversized datasets (stretch goal, not core)

Explicitly **out of scope** for this event (see §21): arc-variable QUBO, IBM Quantum
hardware, a general `OptimizationContext` refactor, Docker/deployment work, a Factory
pattern for vehicle creation. These add engineering ceremony without judge-visible
payoff in the time available — cutting them is what makes the above 5 objectives
actually finishable.

---

# 3. Architecture

```text
                 FastAPI

          REST API Layer  (all routes under /api — matches v1's existing prefix)
                 │
      ┌──────────┴──────────┐
      │                     │
 Upload / Solve APIs   Analytics / Benchmark APIs
 (v1, unchanged)       (v2, new)
      │                     │
      └──────────┬──────────┘
                 │
        Optimization Pipeline
                 │
 ┌─────────────────────────────────┐
 │ Validation           (v1)        │
 │ Demand Analysis      (v2, new)   │
 │ Distance Matrix      (v1)        │
 │ Clustering           (v1 core,   │
 │                       v2 wires   │
 │                       it in)     │
 │ OR-Tools             (v1)        │
 │ QUBO (assignment-var) (v1)       │
 │ QAOA                 (v1)        │
 │ Repair / Fallback    (v1)        │
 │ Decision Engine      (v2, new)   │
 │ Benchmark            (v2, new)   │
 │ Sustainability       (v1)        │
 │ Analytics            (v2, new)   │
 └─────────────────────────────────┘
```

---

# 4. Folder Structure

Only additions on top of the existing v1 tree are new; everything already in v1
(`ortools_solver.py`, `qubo.py`, `qaoa_solver.py`, `repair.py`, `emission.py`,
`dataset.py`, `distance.py`, models, upload/classical/quantum/compare routes)
stays exactly where it is.

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── routes/
│   │   ├── upload.py            (v1, unchanged)
│   │   ├── classical.py         (v1, unchanged)
│   │   ├── quantum.py           (v1, unchanged)
│   │   ├── compare.py           (v1, unchanged)
│   │   ├── benchmark.py         (NEW)
│   │   ├── analytics.py         (NEW)
│   │   └── fleet.py             (NEW — small, exposes demand analysis)
│   │
│   ├── services/
│   │   ├── dataset.py           (v1, unchanged)
│   │   ├── distance.py          (v1, unchanged)
│   │   ├── ortools_solver.py    (v1, unchanged)
│   │   ├── qubo.py              (v1, unchanged — assignment-variable encoding)
│   │   ├── qaoa_solver.py       (v1, unchanged)
│   │   ├── repair.py            (v1, unchanged)
│   │   ├── emission.py          (v1, unchanged)
│   │   ├── demand.py            (NEW — small, see §6.1)
│   │   ├── decision_engine.py   (NEW — see §14)
│   │   ├── benchmark.py         (NEW — see §15)
│   │   └── analytics.py         (NEW — see §17)
│   │
│   ├── models/                  (v1, unchanged)
│   └── utils/                   (v1, unchanged)
│
├── tests/
│   ├── test_decision_engine.py  (NEW)
│   ├── test_benchmark.py        (NEW)
│   └── ...                      (existing v1 tests, unchanged)
│
├── depot.json
└── requirements.txt
```

No `config/settings.py` / `config/constants.py` split and no top-level
`OptimizationContext` object this round — see §6 and §21 for why, and what a
minimal version of each looks like if time permits.

---

# 5. Service Responsibilities

| Service | Status | Responsibility |
|---|---|---|
| `dataset.py` | v1 | Parse uploaded CSV |
| `distance.py` | v1 | Distance matrix generation |
| `ortools_solver.py` | v1 | Classical optimization |
| `qubo.py` | v1 | Build QUBO (assignment-variable `y[i,k]`) |
| `qaoa_solver.py` | v1 | Execute quantum optimization, multi-run |
| `repair.py` | v1 | Fix infeasible QAOA solutions / NN fallback |
| `emission.py` | v1 | Fuel & CO₂ calculations |
| `demand.py` | **NEW** | Total demand vs. fleet capacity pre-check |
| `decision_engine.py` | **NEW** | Score feasible routes, pick + explain a winner |
| `benchmark.py` | **NEW** | Structure OR-Tools vs. QAOA stats for the dashboard |
| `analytics.py` | **NEW** | Fleet / routing / sustainability KPIs for the dashboard |

`clustering` is **not** a new service — v1's `dataset.py` already contains
`cluster_customers()` (k-means). V2's only job here is to make sure the live
`/api/quantum` pipeline actually calls it when `N > QAOA_CUSTOMER_LIMIT`, instead of
only using it for the frontend's advisory notice.

---

# 6. Passing Data Between Services

Rather than introducing a single large `OptimizationContext` god-object touched by
every service (high refactor risk, low judge-visible payoff, and every existing v1
function signature would need to change), v2 uses a small, focused result object
per new service — each one takes the specific v1 outputs it needs as arguments and
returns a typed result. This keeps the blast radius of "adding v2" close to zero for
the working v1 code.

```python
# services/decision_engine.py
@dataclass
class DecisionResult:
    winner: str                  # "classical" | "quantum"
    reason: str                  # human-readable justification
    classical_score: float
    quantum_score: float
    scoring_breakdown: dict       # per-metric normalized contributions
```

```python
# services/benchmark.py
@dataclass
class BenchmarkResult:
    classical: dict
    quantum: dict
    winner: str
    decision: DecisionResult
```

If, and only if, there is spare time after the 5 core v2 objectives are done, these
can be consolidated into one shared context object as a code-quality pass — but that
consolidation is explicitly a stretch goal, not a dependency for anything else in
this document.

## 6.1 Demand Analysis (`demand.py`)

Intentionally minimal — one function, called right after upload validation:

```python
def check_fleet_capacity(customers, vehicle_config) -> dict:
    total_demand = sum(c.demand for c in customers)
    total_capacity = sum(vehicle_config.capacities_list)
    return {
        "total_demand": total_demand,
        "total_capacity": total_capacity,
        "sufficient": total_capacity >= total_demand,
        "utilization_pct": round(total_demand / total_capacity * 100, 1)
            if total_capacity > 0 else None,
    }
```

Surfaced in the `/api/upload` response as an early, honest warning ("your fleet
capacity is only 82% of total demand — OR-Tools/QAOA will fail to find a feasible
solution") rather than letting the person discover it only when a solve fails later.

---

# 7. API Design

## Existing endpoints (v1) — unchanged, all under `/api`

```
POST /api/upload
POST /api/classical
POST /api/quantum
GET  /api/compare
```

## New endpoints (v2) — corrected to use the same `/api` prefix as v1

```
GET  /api/benchmark
GET  /api/analytics
GET  /api/fleet
GET  /api/health
```

`/api/simulate` from the previous draft is dropped — it duplicated
`/api/classical` + `/api/quantum` + `/api/compare` without adding new behavior.
If a single "run everything" convenience endpoint is wanted for the demo, it should
be a thin wrapper that calls the three existing endpoints in sequence and returns
`/api/benchmark`'s result — not a new pipeline.

### `GET /api/benchmark`

Requires both `/api/classical` and `/api/quantum` to have been run first (same
precondition as the existing `/api/compare`). Returns:

```json
{
  "classical": {
    "distance_km": 31.2,
    "fuel_l": 3.5,
    "co2_kg": 8.1,
    "runtime_s": 0.8,
    "feasible": true
  },
  "quantum": {
    "distance_km": 29.8,
    "fuel_l": 3.3,
    "co2_kg": 7.6,
    "runtime_s": 4.2,
    "feasible": true,
    "fallback_used": false,
    "objective_best": 29.8,
    "objective_mean": 30.4,
    "objective_variance": 0.62,
    "runs": 5
  },
  "winner": "quantum",
  "decision": {
    "reason": "Quantum route is 4.5% shorter and feasible without fallback; runtime cost accepted given simulator context.",
    "classical_score": 0.61,
    "quantum_score": 0.74,
    "scoring_breakdown": {
      "distance": 0.42,
      "runtime": -0.08,
      "fuel_co2_note": "excluded from score — linear in distance, not independent signal"
    }
  }
}
```

### `GET /api/analytics`

No new computation of its own — reshapes whatever combination of
`classical_result` / `quantum_result` / `benchmark` is currently in app state.
Returns `null` for any section whose prerequisite hasn't run yet (mirrors how
`/api/compare` already handles partial state in v1).

```json
{
  "fleet": {
    "vehicles_used": 3,
    "total_vehicles_configured": 3,
    "average_utilization_pct": 78.4
  },
  "routing": {
    "average_route_km": 10.4,
    "longest_route_km": 14.1,
    "solver_used": "quantum"
  },
  "customers": {
    "delivered": 6,
    "total": 6
  },
  "optimization": {
    "runtime_s": 4.2,
    "runs": 5,
    "objective_variance": 0.62
  },
  "sustainability": {
    "fuel_l": 3.3,
    "co2_kg": 7.6,
    "co2_saved_pct": 6.2
  }
}
```

### `GET /api/fleet`

Wraps `demand.py`'s `check_fleet_capacity()` against the currently uploaded
dataset + vehicle config:

```json
{
  "total_demand": 79,
  "total_capacity": 96,
  "sufficient": true,
  "utilization_pct": 82.3
}
```

### `GET /api/health`

```json
{ "status": "ok", "version": "2.1.0" }
```

(v1 already has this at the app level — v2 just versions it correctly.)

---

# 8. Pipeline (corrected order)

1. Upload CSV
2. Validate (v1, unchanged)
3. Compute demand statistics (v2 — informational, does not block the pipeline)
4. Generate distance matrix (v1, unchanged)
5. Cluster customers, **only if** `N > QAOA_CUSTOMER_LIMIT` (v1's existing k-means,
   now actually wired into the live solve path, not just the frontend notice)
6. Run OR-Tools (v1, unchanged)
7. Build QUBO — assignment-variable encoding (v1, unchanged)
8. Run QAOA, multi-run (v1, unchanged)
9. **Repair / fallback the QAOA result** (v1, unchanged) — this must complete
   before step 10
10. Decision Engine scores the two *feasible* results (v2, new)
11. Benchmark records both results + the decision (v2, new)
12. Sustainability / emission calculations (v1, unchanged, reused for both solvers)
13. Analytics reshapes everything above for the dashboard (v2, new)

This is the single canonical ordering for the whole document — Part 2's diagrams
are kept consistent with it (previously, §1/§22's diagram and §8's numbered list
disagreed about whether Repair or the Decision Engine ran first; this version
fixes that by defining it once, here).

---

# 9. Design Patterns

Kept intentionally minimal — patterns should earn their place by solving a real
problem in the 36-hour window, not for their own sake.

- **Strategy Pattern** — OR-Tools and QAOA are already independent, swappable
  solve strategies in v1; the Decision Engine is the piece that picks between
  their outputs. No further strategy abstraction needed.
- **Pipeline Pattern** — the ordered pipeline in §8 is deliberately just a
  sequence of function calls in `main.py` / the relevant route handler, not a
  formal pipeline framework. Introducing one would cost more time than it saves
  at this scale.

Dropped from the previous draft: **Factory Pattern** for vehicle/solver creation.
v1's `VehicleConfig` model and the two existing solver modules already do this
job adequately; a formal factory adds indirection without a concrete benefit for
a two-solver, single-vehicle-model system.

---

# 10. End of Part 1

Part 2 covers, in priority order for the remaining hackathon time:

1. Decision Engine internals (fixed scoring — §14)
2. Benchmark framework (§15)
3. Analytics engine (§17)
4. Demand analysis details (already scoped small in §6.1 above)
5. Clustering integration notes (§13, trimmed to what's realistic)
6. Deployment / future scope (§19–21, explicitly marked "after the demo, not before")
