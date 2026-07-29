# frontend_v2.md — Part 2
# UI Components & User Experience (corrected)

> Continuation of Part 1. Status tags carried over: **[Shipped]**, **[V2 — Planned]**, **[Descoped]**.

---

# 11. User Journey

```text
Landing
   │
Upload Dataset
   │
Fleet Validation        ← uses /api/fleet [V2 — Planned], not a frontend calculation
   │
Run Classical
   │
Run Quantum
   │
Benchmark                ← /api/benchmark, Decision Engine verdict
   │
Analytics                ← /api/analytics
```

---

# 12. Upload Page — [Shipped]

## Components

- Drag & Drop CSV Upload
- Browse File Button
- Vehicle Configuration Form
- Dataset Preview Table
- Fleet Capacity Card — **[V2 — Planned]**: call `GET /api/fleet` after config
  changes and show `sufficient: false` as an inline warning before the user
  even uploads, instead of only discovering insufficient capacity after a solver run
- Upload Progress

## Validation

- Invalid CSV format
- Missing columns
- Invalid coordinates
- Empty dataset

---

# 13. Dashboard — [Shipped]

The dashboard is the application's home after a successful upload. It runs the
solvers and shows a quick overview; the deep-dive comparison and KPIs live on
the dedicated Benchmark and Analytics pages (§15, §17) to keep this page
focused and fast.

Widgets:

- Total Customers
- Vehicles
- Distance
- Runtime
- Fuel
- CO₂
- Selected Solver
- "View Benchmark" / "View Analytics" links once results exist

Layout

```text
Navbar
│
Action buttons (Run Classical / Run Quantum / Compare / Reset)
│
KPI Cards
│
Map
│
→ links to Benchmark / Analytics
```

---

# 14. Route Visualization — [Shipped]

Technology

- React Leaflet

Display

- Depot
- Customer markers
- Vehicle routes
- Route legend

Features

- Zoom
- Pan
- Vehicle color coding
- Marker popups

---

# 15. Benchmark Page — [V2 — Planned]

Dedicated route, `GET /api/benchmark`. Split-screen comparison, gated behind
both solvers having run (matching the endpoint's own precondition):

| Classical | Quantum |
|-----------|----------|
| Distance | Distance |
| Runtime | Runtime |
| Fuel | Fuel |
| CO₂ | CO₂ |
| Feasible | Feasible / `fallback_used` |

If the endpoint 4xxs because one or both solvers haven't run yet, show an
inline prompt linking back to the Dashboard — don't treat it as an error state.

Decision Engine panel (§16) is displayed above the comparison table, not below —
the winner and reason are the headline; the raw numbers are supporting detail.

---

# 16. Decision Engine Panel — [V2 — Planned]

Purpose: render `backend_v2.md` §14's `decision` object exactly as returned —
**do not** recompute a score or a winner client-side.

Response shape (`GET /api/benchmark`'s `decision` field):

```json
{
  "reason": "Quantum route is 4.5% shorter and feasible without fallback; runtime cost accepted given simulator context.",
  "classical_score": 0.61,
  "quantum_score": 0.74,
  "scoring_breakdown": {
    "distance": 0.42,
    "runtime": -0.08,
    "fuel_co2_note": "excluded from score — linear in distance, not independent signal"
  }
}
```

Display

- **Winner** badge (`benchmark.winner`: `"classical"` | `"quantum"`)
- **Reason** — the one sentence from `decision.reason`, shown verbatim, largest text on the panel
- **Score bar** — `classical_score` vs `quantum_score`, both already normalized to `[0, 1]`
- **Breakdown** — `scoring_breakdown.distance` / `.runtime` as small labeled bars; render
  `fuel_co2_note` as plain muted text explaining why fuel/CO₂ aren't scored here
  (they're still shown in full elsewhere — Benchmark table, Analytics sustainability
  section — just not double-counted in the decision score itself)
- If `quantum.feasible === false`: skip the score bars entirely and show only the reason
  ("Quantum route infeasible even after repair/fallback") — the backend's `decide()`
  short-circuits in this case and there's nothing meaningful to normalize

Do not build a client-side checklist of "✓ Shorter route / ✓ Feasible / ✓ Lower
fuel" — that was the v2.1 draft's approach and it re-implements the backend's
scoring in a way that can silently drift out of sync with `decision_engine.py`.
The backend already decided; the frontend's job is to explain the decision, not
re-derive one.

---

# 17. Analytics Dashboard — [V2 — Planned]

Dedicated route, `GET /api/analytics`. Reshapes existing backend numbers —
no new frontend computation, including no client-side utilization math.

Response shape:

```json
{
  "fleet": { "vehicles_used": 3, "total_vehicles_configured": 3, "average_utilization_pct": 78.4 },
  "routing": { "average_route_km": 10.4, "longest_route_km": 14.1, "solver_used": "quantum" },
  "customers": { "delivered": 6, "total": 6 },
  "optimization": { "runtime_s": 4.2, "runs": 5, "objective_variance": 0.62 },
  "sustainability": { "fuel_l": 3.3, "co2_kg": 7.6, "co2_saved_pct": 6.2 }
}
```

Sections

| Section | Fields shown |
|---|---|
| Fleet | Vehicles Used / Total Configured, Average Utilization % |
| Routing | Average Route (km), Longest Route (km), Solver Used |
| Customers | Delivered / Total |
| Optimization | Runtime, Runs, Objective Variance |
| Sustainability | Fuel, CO₂, % CO₂ Saved |

Any section whose prerequisite hasn't run yet arrives as `null` — render that
section as a locked/greyed card with a one-line "run X first" hint rather than
hiding it, so the page's shape doesn't jump around as results come in.

Use Chart.js where a chart adds value (e.g. a small runtime-over-runs
sparkline for `optimization.objective_variance`); most of this page is cards,
not charts.

---

# 18. Optimization Timeline — [Shipped]

Visual pipeline

```text
Upload
 ↓
Validation
 ↓
Distance Matrix
 ↓
OR-Tools
 ↓
QUBO
 ↓
QAOA
 ↓
Repair
 ↓
Benchmark (Decision Engine)
 ↓
Analytics
```

Completed stages should highlight progressively during execution.

---

# 19. Fleet Dashboard — [V2 — Planned]

Uses `GET /api/fleet`:

```json
{ "total_demand": 79, "total_capacity": 96, "sufficient": true, "utilization_pct": 82.3 }
```

Each vehicle card shows

- Capacity
- Current Load
- Distance
- Fuel
- CO₂

Fleet summary displays `utilization_pct` from the endpoint directly — do not
recompute utilization from `vehicleConfig` client-side, since the backend's
`demand.py` is the single source of truth once a dataset is uploaded.

---

# 20. Scenario Simulator — [V2 — Planned, corrected]

The v2.1 draft implied a dedicated re-simulate endpoint. `backend_v2.md` §7
explicitly drops `/api/simulate` as a duplicate pipeline, so this feature is
corrected to reuse the existing endpoints rather than wait on a new one:

Interactive controls

- Customer count
- Vehicle capacity
- Fuel rate

After modification

```text
1. POST /api/upload   (re-submit with the modified vehicle config)
2. POST /api/classical
3. POST /api/quantum
4. GET  /api/benchmark
```

No new backend endpoint is required. The frontend just re-triggers the same
sequence it already calls from the Dashboard, using the updated
`vehicleConfig` from the Scenario Simulator's controls.

---

# 21. Green Logistics Score — [Descoped]

Removed from v2 scope. `backend_v2.md` §16 explains why: a standalone "green
score" computed from distance/fuel/CO₂/utilization would be a linear function
of distance under the current single-blended-fuel-rate fleet model — the exact
redundancy flaw the corrected Decision Engine (§14 / §16 here) was fixed to
avoid. Adding it back on the frontend, even as "just a UI widget," would
either duplicate the Decision Engine's score under a different name or invent
a new formula the backend never validated.

This becomes real future scope once the backend supports a genuine
per-vehicle-type CO₂ breakdown (e.g. "3.3 kg saved specifically from using
Electric Vans") — see the Future Roadmap in Part 3. Until then, sustainability
figures are shown as-is (fuel, CO₂, % saved) in the Analytics page's
Sustainability section (§17) — no composite score on top of them.

---

# 22. Responsive Design

Support

- Desktop
- Tablet
- Presentation display

Use responsive cards; no collapsible sidebar since none exists (§9, Part 1).

---

# 23. Loading & Error States

Loading

- Skeleton cards
- Spinner during optimization
- Distinct loading labels per stage (`Running OR-Tools…`, `Generating QUBO…`, `Running QAOA…`) — **[Shipped]** on the Dashboard already; reuse the same pattern for Benchmark/Analytics fetches

Errors

- Network failure
- Backend unavailable
- Invalid upload
- `/api/benchmark` called before both solvers ran — treat as a guided prompt, not a generic error (§15)

Always provide retry actions.

---

# 24. End of Part 2

Next Part:

- Architecture diagrams
- Sequence diagrams
- Component diagrams
- ADRs
- Testing strategy
- Configuration
- Deployment
- Future roadmap
