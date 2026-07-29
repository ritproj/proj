
# backend_v2.md — Part 2

> Continuation of Part 1. Version 2.1 (revised).
> Every section below has been checked against what the v1 codebase actually does —
> see the "v1 reality check" note under each section that touches the existing
> solver.

---

# 11. QUBO Formulation — v1's encoding stays, no rewrite

**v1 reality check:** the working backend already builds a QUBO using an
**assignment-variable** encoding, not the arc-variable encoding this section used
to describe. This matters because arc variables are what actually blow up:

```
x(i, j, v) = 1 if vehicle v travels from customer i to customer j

Variable count ≈ N² × K
```

For a 15-customer / 3-vehicle instance that's **~675 binary variables** — many
orders of magnitude past what a local Aer simulator can handle (v1's own QAOA
solver hard-rejects anything over 24 variables). Re-adopting this encoding would
not be a v2 upgrade; it would break the quantum path entirely.

v1's actual, working encoding — kept as-is for v2:

```
y(i, k) = 1 if customer i is assigned to vehicle k
Variable count = N × K
```

For 6 customers / 2 vehicles that's 12 variables — comfortably within budget.
Route ordering within each vehicle's assigned set is handled afterward by a
nearest-neighbor pass (`repair.py` / `qubo.py`'s route-cost estimator), which is
exactly what avoids needing MTZ subtour-elimination variables.

### Objective (unchanged from v1)

```
H_distance ≈ Σ_k  nn_route_cost(customers assigned to vehicle k)
```

### Constraint penalties (unchanged from v1)

```
H_assign   : each customer assigned to exactly one vehicle
H_capacity : each vehicle's assigned demand ≤ its capacity
```

```
H = H_distance + λ · H_assign + λ · H_capacity
λ = PENALTY_MULTIPLIER × max_edge_weight   (PENALTY_MULTIPLIER = 10 in v1)
```

**If you want the richer arc-based formulation for a future/research write-up**,
scope it explicitly as hardware-scale-only (real IBM Quantum backends, not the
local simulator) and file it under §21 Future Scope. It is not part of this
event's deliverable.

---

# 12. QAOA Execution Pipeline

**v1 reality check:** v1 already implements this pipeline, including the
random-sampling fallback if Qiskit isn't importable, and already runs multiple
QAOA instances per solve for benchmarking. Nothing here is new — this section
documents it so the Decision Engine and Benchmark services (§14–15) know exactly
what data they can rely on.

```text
QUBO (assignment-variable, from §11)
  │
QuadraticProgram → QuadraticProgramToQubo (Qiskit Optimization)
  │
QAOA(sampler=AerSampler(), optimizer=COBYLA(maxiter=200), reps=QAOA_LAYERS)
  │
MinimumEigenOptimizer(qaoa).solve(...)
  │
Best bitstring + objective value
  │
Route Decoder (repair.py: decode_bitstring)
```

### Configuration (matches v1, not the previous draft's numbers)

| Setting | v1 value | Notes |
|---|---|---|
| Layers (p) | 3 | v1 uses p=3, not p=1/p=2 as previously drafted — keep it, it's already tuned |
| Optimizer | COBYLA, maxiter=200 | unchanged |
| Runs | 5 independent runs per solve | for mean/best/variance reporting |
| Shots (fallback path only) | 1024 | used only when Qiskit is unavailable and the solver falls back to random sampling |
| Simulator | Qiskit Aer (`AerSampler`) | unchanged |
| **Hard qubit/customer cap** | **`n_vars > 24` rejected; `QAOA_CUSTOMER_LIMIT = 8` customers** | this is the real, tested limit — see §13 for why the "small/medium/large" strategy must respect it, not the reverse |

Stored per run (already implemented, exposed via `/api/quantum` and now also via
`/api/benchmark`):

- `runtime_s`, `objective_best`, `objective_mean`, `objective_variance`, `runs`,
  `feasible`, `fallback_used`, decoded route.

No change needed here beyond making sure `/api/benchmark` reads these same fields
rather than recomputing anything.

---

# 13. Hybrid Optimization Strategy — thresholds corrected to match v1's actual limits

**Flaw fixed:** the previous draft set a "<15 customers → Pure QAOA" threshold.
v1's tested, working limit is **8 customers** (`QAOA_CUSTOMER_LIMIT = 8`, and a
hard `n_vars > 24` rejection inside the solver). Setting the threshold at 15 would
mean the "hybrid strategy" immediately routes real datasets into a solver that
rejects them — the opposite of the intended effect.

Corrected strategy, using v1's real constants everywhere:

## Small instance (≤ `QAOA_CUSTOMER_LIMIT`, i.e. ≤ 8 customers, ≤ 3 vehicles)

→ Run **both** OR-Tools and QAOA in full, exactly as v1 already does.
→ This is the only tier where a genuine quantum-vs-classical comparison happens.

## Medium (9–30 customers)

→ Run OR-Tools on the full instance (its only real limit is the 5-second time
  budget already configured in `ortools_solver.py`).
→ Cluster with v1's existing `cluster_customers()` (k-means) into groups of
  ≤ 8 customers each.
→ Run QAOA on **each cluster independently**, then concatenate the resulting
  per-cluster routes into the final quantum solution.
→ This is "QAOA refinement" in the sense that it's still QAOA doing real work,
  just partitioned — not OR-Tools output being locally perturbed by a quantum
  step, which the previous draft's wording implied but never specified how to do.

## Large (> 30 customers)

→ Cluster (same k-means), same as Medium.
→ **OR-Tools only** per cluster; QAOA is skipped entirely and the UI should say
  so plainly ("dataset too large for the quantum demo path — showing classical
  results only for clusters beyond the QAOA-viable size").
→ This keeps the demo honest instead of silently degrading to a fallback
  heuristic that looks like "quantum" in the UI but isn't.

Benefits (unchanged from previous draft, still valid):

- Practical scalability without lying about what ran
- Honest use of quantum resources — the UI's existing `fallback_used` /
  `feasible` flags extend naturally to a new `quantum_skipped: bool` field for
  the Large tier
- Faster overall execution, since OR-Tools handles what it's good at

---

# 14. Decision Engine — fixed scoring model

**Flaw fixed:** the previous scoring formula —

```
Score = 0.45 × Distance + 0.20 × Fuel + 0.20 × CO₂ + 0.15 × Runtime
```

— double- and triple-counts the same underlying signal. In v1, `fuel_l =
distance_km × blended_fuel_rate` and `co2_kg = fuel_l × 2.31`. Both are exact
linear functions of distance for a given vehicle mix, so weighting all three
independently doesn't produce a genuine multi-objective score — it's ~85%
"distance, restated three times at different scales" plus 15% runtime. It also
mixes raw units (km, L, kg, seconds) without normalizing them first, so the
stated weights don't mean what they appear to.

### Corrected approach

Score on **two independent signals only** — distance (the thing the solvers are
actually optimizing) and runtime (the real cost tradeoff worth surfacing) — each
normalized to a comparable scale before weighting:

```python
def normalize(classical_value: float, quantum_value: float) -> tuple[float, float]:
    """
    Min-max normalize a pair of values to [0, 1], where 1 = better (lower is
    better for both distance and runtime here). Returns (classical_norm, quantum_norm).
    """
    lo, hi = min(classical_value, quantum_value), max(classical_value, quantum_value)
    if hi == lo:
        return 1.0, 1.0  # tie — both score full marks on this metric
    return (
        1.0 - (classical_value - lo) / (hi - lo),
        1.0 - (quantum_value - lo) / (hi - lo),
    )

DISTANCE_WEIGHT = 0.75
RUNTIME_WEIGHT  = 0.25

def score_candidate(distance_norm: float, runtime_norm: float) -> float:
    return DISTANCE_WEIGHT * distance_norm + RUNTIME_WEIGHT * runtime_norm
```

```python
def decide(classical: dict, quantum: dict) -> DecisionResult:
    # Reject infeasible routes before scoring — quantum must have already
    # been through repair/fallback (§8, step 9) by the time it reaches here.
    if not quantum.get("feasible", False):
        return DecisionResult(
            winner="classical",
            reason="Quantum route infeasible even after repair/fallback.",
            classical_score=1.0, quantum_score=0.0,
            scoring_breakdown={"distance": None, "runtime": None},
        )

    c_dist_n, q_dist_n = normalize(classical["distance_km"], quantum["distance_km"])
    c_rt_n,   q_rt_n   = normalize(classical["runtime_s"],   quantum["runtime_s"])

    c_score = score_candidate(c_dist_n, c_rt_n)
    q_score = score_candidate(q_dist_n, q_rt_n)

    winner = "quantum" if q_score > c_score else "classical"
    reason = _explain(classical, quantum, winner, q_dist_n, q_rt_n)

    return DecisionResult(
        winner=winner,
        reason=reason,
        classical_score=round(c_score, 3),
        quantum_score=round(q_score, 3),
        scoring_breakdown={"distance": round(q_dist_n, 3), "runtime": round(q_rt_n, 3)},
    )
```

**Fuel and CO₂ are not dropped from the product** — they still appear in full in
`/api/compare`, `/api/benchmark`, and the frontend's Sustainability Summary,
exactly as v1 already shows them. They're just excluded from the *decision score*
specifically, because scoring them again adds no new information once distance is
already weighted in. If a future version wants fuel/CO₂ to matter independently —
e.g., because different vehicle types have different rates and a mixed fleet
could make fuel-optimal and distance-optimal routes diverge — that's a real,
addressable case, but it requires the routes to actually differ in per-vehicle
composition, not just in total distance. Flag it in §21 as future scope rather
than pretending the current single-fleet-rate setup already needs it.

### Output (matches the `/api/benchmark` schema in Part 1 §7)

- `winner`: `"classical"` or `"quantum"`
- `reason`: a one-sentence, judge-readable explanation (not just the score)
- `classical_score`, `quantum_score`: normalized, in `[0, 1]`
- `scoring_breakdown`: the per-metric normalized values that produced the score

---

# 15. Benchmark Engine

Metrics (all already computed by v1, none newly invented):

- Runtime (`runtime_s`, both solvers)
- Distance (`distance_km`, both solvers)
- Fuel (`fuel_l`, both solvers)
- CO₂ (`co2_kg`, both solvers)
- QAOA-specific: `objective_best`, `objective_mean`, `objective_variance`, `runs`
- Feasibility (`feasible`, `fallback_used` for quantum)

`benchmark.py`'s only job is to call the Decision Engine (§14) and package
everything into the response shape already specified in Part 1 §7:

```json
{
  "classical": { "...": "as returned by /api/classical" },
  "quantum":   { "...": "as returned by /api/quantum" },
  "winner": "quantum",
  "decision": { "reason": "...", "classical_score": 0.61, "quantum_score": 0.74, "scoring_breakdown": {} }
}
```

Exposed via `GET /api/benchmark` (corrected prefix — see Part 1 §7). Vehicle
utilization is intentionally reported in `/api/analytics` (§17) rather than here,
to keep this endpoint focused on the classical-vs-quantum comparison judges will
actually look at.

---

# 16. Sustainability Engine — unchanged, reused as-is

No changes from v1. `emission.py` already implements:

```
Fuel = Distance × blended_fuel_rate   (blended across the configured fleet mix)
CO₂  = Fuel × 2.31                    (kg CO₂ per litre of petrol)
```

Plus the savings calculation already in `compute_savings()`:

```
distance_saved_pct, fuel_saved_pct, co2_saved_pct
```

v2 does not add a separate "Green Score" metric this round — it would be another
linear function of distance (same redundancy problem as §14's original scoring
formula) unless it's given an independently-varying input, which the current
single-blended-rate fleet model doesn't provide. If a genuine per-vehicle-type
breakdown becomes useful later (e.g. "3.3 kg CO₂ saved specifically by using more
Electric Vans"), that's real future scope — see §21.

---

# 17. Analytics Engine

Reshapes existing v1 + v2 outputs into the dashboard-ready sections defined in
Part 1 §7's `/api/analytics` schema. No new computation beyond simple aggregation:

| Section | Fields | Source |
|---|---|---|
| Fleet | vehicles used, total configured, avg utilization | `vehicle_config` + solver's `vehicle_loads` |
| Routing | avg route length, longest route, solver used | solver route lists + distance matrix |
| Customers | delivered, total | `len(customers)`, route node counts |
| Optimization | runtime, runs, objective variance | QAOA result fields (v1) |
| Sustainability | fuel, CO₂, % saved | `emission.py` (v1, unchanged) |

Returns partial data (matching sections `null`) if only one solver has run yet —
same pattern v1's `/api/compare` already uses for partial state, kept consistent.

---

# 18. Logging & Configuration — trimmed to what's actually needed

The previous draft proposed a full `config/settings.py` + `config/constants.py`
split with `DEBUG` / `SIMULATOR` / `IBM_BACKEND` / `MAX_QAOA_DEPTH` environment
variables. For a 36-hour hackathon with a single local Aer simulator target and
no IBM hardware integration in scope (§21), this is premature — there's nothing
in this document that actually reads `IBM_BACKEND` or varies `MAX_QAOA_DEPTH` at
runtime.

**Minimal version actually worth building:**

```python
# app/config.py  (single file, not a package)
QAOA_CUSTOMER_LIMIT = 8      # already a constant in qaoa_solver.py — just import it
DEBUG = False                 # toggled via one env var if genuinely needed for the demo
```

Logging: use Python's standard `logging` module at `INFO` level for the pipeline
steps (upload received, solver started/finished, repair triggered, decision made)
and `WARNING`/`ERROR` for anything user-facing that fails. Persisting optimization
summaries to a file is a reasonable stretch goal (helps debug a flaky demo run)
but is not worth building a schema for — dumping the `/api/benchmark` JSON to a
timestamped log file on each call is sufficient.

---

# 19. Deployment — explicitly post-demo

Development target (what actually needs to work for the judged demo):

```
React (Vite dev server) + FastAPI (uvicorn --reload) + Qiskit Aer, all local
```

Nothing beyond this is needed for the hackathon. The following are real,
reasonable next steps for the project **after** the event, not before:

```
React → FastAPI → IBM Quantum Runtime → Cloud Storage
```

Containerizing with Docker is similarly deferred — it protects against "works on
my machine" for a multi-person team pulling the repo, which is a legitimate
concern, but only worth the setup time if the team is actually splitting work
across machines during the 36 hours. If everyone's demoing from one laptop,
skip it.

---

# 20. 36-Hour Hackathon Roadmap — reordered by judge-visible payoff per hour

## Before Event
- v1 backend and frontend confirmed stable (already true per the last review)
- Test datasets ready (`sample_customers.csv` already exists at the right scale)

## Day 1 (build order, highest payoff first)
1. **Decision Engine** (§14) — cheap, and directly produces the "winner + why"
   card that's the single most judge-legible artifact in the whole project
2. **Benchmark endpoint** (§15) — mostly wiring, since all the underlying data
   already exists in v1
3. **Analytics endpoint** (§17) — reshaping, not new computation
4. **Demand analysis** (§6.1) — small, but catches a real failure mode
   (undersized fleet) before it confuses a live demo
5. **Clustering wiring** (§13) — only if steps 1–4 land with time to spare;
   the existing hard customer cap is the safety net either way

## Night
- Bug fixing against the corrected pipeline order (§8)
- Verify the Decision Engine's normalization doesn't misbehave on edge cases
  (ties, one solver failing entirely)
- Re-run v1's existing test suite to confirm nothing regressed (see §0)

## Day 2
- Final demo rehearsal
- Slides
- Practice explaining *why* the Decision Engine picked its winner in one sentence
  per test dataset — this is the story that sells the project

---

# 21. Future Scope (explicitly deferred, not this event's work)

- IBM Quantum Hardware execution (the arc-variable QUBO from the earlier draft
  belongs here, scoped to hardware-scale instances only)
- Multiple depots
- Time windows (CVRPTW)
- Electric-vehicle energy-based fuel model (v1's fuel rate table already has an
  `Electric Van` placeholder at 0.00 L/km for this)
- Live traffic / weather-aware routing
- Reinforcement-learning-assisted routing
- Per-vehicle-type "Green Score" breakdown (see §16) — genuinely useful once the
  fleet model supports routes that vary in vehicle-type composition, not before
- Full `OptimizationContext` consolidation (§6) as a code-quality pass
- Dockerized deployment (§19)

---

# 22. Final Backend Workflow (corrected, matches Part 1 §8 exactly)

```text
CSV Upload
    │
Validation
    │
Demand Analysis                (v2 — informational)
    │
Distance Matrix
    │
Customer Clustering            (only if N > QAOA_CUSTOMER_LIMIT)
    │
 ┌──────────────┬──────────────┐
 │  OR-Tools    │  QUBO → QAOA  │   (run independently)
 └──────────────┴──────────────┘
    │
Repair / Fallback               (on the QAOA result, before scoring — v1, unchanged)
    │
Decision Engine                 (v2 — scores only feasible routes)
    │
Benchmark                       (v2 — packages both results + the decision)
    │
Sustainability / Emission       (v1, unchanged, reused for both solvers)
    │
Analytics                       (v2 — dashboard-ready reshaping)
    │
REST API  (all under /api)
    │
React Dashboard
```

# End of backend_v2.md
