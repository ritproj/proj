# frontend_v2.md — Part 1
# GreenRoute Frontend Architecture V2 (corrected)

> Version: 2.2 — corrected against `backend_v2.md`'s actual API surface and the
> shipped `frontend/src` codebase, not just the original 36-hour plan.
> Purpose: scalable React frontend, presentation-only, that consumes the
> backend's corrected v2 endpoints without duplicating any solver or scoring logic.

---

# 0. Corrections from the v2.1 draft

The previous draft was written speculatively, before the backend's v2 corrections
landed and before the frontend's shipped structure stabilized. Fixed here:

| # | Issue in v2.1 draft | Correction |
|---|---|---|
| 1 | Tech stack listed **Recharts** for charts | Shipped code uses **Chart.js + react-chartjs-2** for the benchmark bar chart; Recharts is not installed. Doc now matches code. |
| 2 | Layout described `Header / Sidebar / Main / Footer` | Shipped UI is a single sticky top **Navbar** with inline nav links — no `Sidebar` or `Footer` component exists. Doc corrected. |
| 3 | Global state described three Contexts (`DatasetContext`, `OptimizationContext`, `ThemeContext`) | Shipped code uses **one `AppContext`** holding all app state. There is no theme feature scoped, so `ThemeContext` is dropped rather than left as a stub. |
| 4 | API layer used placeholder function names not tied to real routes | Corrected to call the exact endpoints in `backend_v2.md` Part 1 §7 (`/api/benchmark`, `/api/analytics`, `/api/fleet`, `/api/health`), including the dropped `/api/simulate`. |
| 5 | §21 "Green Logistics Score" was a first-class widget | `backend_v2.md` §16 explicitly descopes this: it's a linear function of distance, the same redundancy flaw the corrected Decision Engine (§14) was fixed to avoid. Moved to Future Roadmap — **not built** — until it has an independent input (e.g. per-vehicle-type CO₂ breakdown). |
| 6 | §20 "Scenario Simulator" implied a dedicated re-simulate endpoint | `backend_v2.md` §7 explicitly drops `/api/simulate` as duplicate pipeline. Corrected to re-run through the existing `/api/upload → /api/classical → /api/quantum → /api/benchmark` sequence. |
| 7 | `/settings` was listed in the routing table with no page design anywhere in Parts 2–3 | Marked **descoped** in §6's routing table until it has an actual spec. Not implemented, not silently assumed done. |

Everything below reflects the corrected state. Sections carry a status tag:
**[Shipped]** exists in code today, **[V2 — Planned]** designed here and ready to
build, **[Descoped]** intentionally not in scope this round.

---

# 1. Design Goals

The frontend should:

- Present optimization results clearly, with the Decision Engine's one-sentence
  reasoning (`backend_v2.md` §14) surfaced prominently — that's the line judges
  read first, not the raw scores.
- Tell a story during the demo: Upload → Dashboard → Benchmark → Analytics.
- Separate UI from business logic — no scoring, no normalization, no emissions
  math in the frontend. All of it lives in the backend and is only *displayed* here.
- Consume backend APIs without duplicating logic or inventing metrics the
  backend doesn't already compute.
- Scale with future features without redesigning the state model.

---

# 2. Technology Stack

| Layer | Technology | Status |
|--------|------------|---|
| Framework | React + Vite | [Shipped] |
| Language | JavaScript (`.jsx`) | [Shipped] — TypeScript was "recommended" in the v2.1 draft but never adopted; dropped from the plan rather than left as an unfulfilled aspiration |
| Styling | Tailwind CSS | [Shipped] |
| Routing | React Router v6 | [Shipped] |
| Charts | **Chart.js + react-chartjs-2** | [Shipped] — corrected from Recharts |
| Maps | Leaflet + react-leaflet | [Shipped] |
| Icons | Lucide React | [Shipped] |
| HTTP | Axios | [Shipped] |

---

# 3. Design Philosophy

The frontend never performs optimization, scoring, or emissions math.

Responsibilities:

- Upload data
- Visualize routes
- Display the backend's Decision Engine verdict in plain language
- Display KPIs computed by `/api/analytics`
- Compare results side by side

All optimization, scoring, and sustainability math remains in FastAPI
(`backend_v2.md` §5, §14, §16). If a number appears on screen, it came from a
response body — the frontend does not recompute or re-derive it, including
percentages and "winner" labels.

---

# 4. High-Level Architecture

```text
React App
    │
Pages
    │
Components
    │
Hooks
    │
API Services
    │
FastAPI Backend (backend_v2.md)
```

---

# 5. Folder Structure

```text
frontend/
└── src/
    ├── assets/
    ├── components/
    │   ├── common/
    │   │   ├── StatsCard.jsx
    │   │   └── ErrorBanner.jsx
    │   ├── dashboard/
    │   ├── map/
    │   │   └── RouteMap.jsx
    │   ├── benchmark/
    │   │   ├── ComparisonTable.jsx
    │   │   ├── ResultChart.jsx
    │   │   └── DecisionEnginePanel.jsx      # [V2 — Planned] renders /api/benchmark's `decision` block
    │   └── analytics/                        # [V2 — Planned] renders /api/analytics sections
    ├── context/
    │   └── AppContext.jsx                    # single context — see §7
    ├── hooks/
    ├── layouts/
    ├── pages/
    │   ├── Landing.jsx
    │   ├── Upload.jsx
    │   ├── Dashboard.jsx
    │   ├── Benchmark.jsx                     # [V2 — Planned]
    │   └── Analytics.jsx                     # [V2 — Planned]
    ├── services/
    │   ├── api.js                            # shared axios instance
    │   ├── upload.js
    │   ├── optimization.js                   # runClassical(), runQuantum(), compareResults()
    │   ├── benchmark.js                      # [V2 — Planned] getBenchmark()
    │   ├── analytics.js                      # [V2 — Planned] getAnalytics()
    │   └── fleet.js                          # [V2 — Planned] getFleetCapacity()
    ├── styles/
    ├── types/
    ├── utils/
    ├── App.tsx
    └── main.tsx
```

No `Sidebar`, `Footer`, or `Settings` page exist yet — see §6.

---

# 6. Routing

| Route | Purpose | Status |
|--------|---------|---|
| `/` | Landing | [Shipped] |
| `/upload` | Dataset upload | [Shipped] |
| `/dashboard` | Run solvers, overview, map | [Shipped] |
| `/benchmark` | Classical vs Quantum + Decision Engine | [V2 — Planned] |
| `/analytics` | Fleet / routing / optimization / sustainability KPIs | [V2 — Planned] |
| `/settings` | Theme & preferences | [Descoped] — no design exists; do not build until specced |

---

# 7. Global State

**One context: `AppContext`** (not three — the v2.1 draft's `DatasetContext` /
`OptimizationContext` / `ThemeContext` split was never built and there's no
theme feature to justify it).

State held:

- `uploadedFile`, `parsedCustomers`, `vehicleConfig`
- `classicalResult`, `quantumResult` — raw `/api/classical` and `/api/quantum` bodies
- `comparisonResult` — `/api/compare` body (v1, kept for the Dashboard's quick "Compare" action)
- `benchmarkResult` — `/api/benchmark` body **[V2 — Planned]**: `{ classical, quantum, winner, decision }`
- `analyticsResult` — `/api/analytics` body **[V2 — Planned]**
- `loadingState`, `error`, `showClusteringNotice`

`benchmarkResult` and `comparisonResult` overlap in purpose (both compare
classical vs quantum). Keep both: `/api/compare` is the v1 quick-check used by
the Dashboard's inline "Compare" button; `/api/benchmark` is the richer,
judge-facing verdict with the Decision Engine's scored reasoning, shown on the
dedicated Benchmark page. Don't merge them into one call — the Dashboard use
case wants a fast partial result, the Benchmark page wants the full decision.

---

# 8. API Layer

```text
services/
    api.ts
    upload.ts
    optimization.ts
    benchmark.ts     [V2 — Planned]
    analytics.ts     [V2 — Planned]
    fleet.ts         [V2 — Planned]
```

Functions, mapped to the exact `backend_v2.md` §7 endpoints:

| Function | Method + Path | Status |
|---|---|---|
| `uploadDataset(file, vehicleConfig)` | `POST /api/upload` | [Shipped] |
| `runClassical()` | `POST /api/classical` | [Shipped] |
| `runQuantum()` | `POST /api/quantum` | [Shipped] |
| `compareResults()` | `GET /api/compare` | [Shipped] |
| `getBenchmark()` | `GET /api/benchmark` | [V2 — Planned] — 4xx if classical/quantum haven't both run; surface as a banner, not a crash |
| `getAnalytics()` | `GET /api/analytics` | [V2 — Planned] — returns `null` per-section for whatever hasn't run yet; render each section independently |
| `getFleetCapacity()` | `GET /api/fleet` | [V2 — Planned] |
| `getHealth()` | `GET /api/health` | [V2 — Planned] — optional footer/status-dot use only |

Note: `/api/simulate` does **not** exist and is not called by anything —
see §20 in Part 2 for how the Scenario Simulator is meant to work without it.

---

# 9. Layout

```text
Navbar (Home · Upload · Dashboard · Benchmark · Analytics)
│
Main Content (per-route page)
```

No Sidebar, no Footer. The Navbar is a single sticky top bar with inline links;
this replaced the originally-planned Header+Sidebar+Footer layout because the
app's page count and content density didn't need the extra chrome.

---

# 10. End of Part 1

Next part:

- Dashboard design
- Route visualization
- Benchmark page + Decision Engine panel
- Analytics dashboard
- Timeline
- Scenario simulator (corrected)
- Fleet capacity check
- Green Logistics Score — why it's descoped, not built
