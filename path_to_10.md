# GreenRoute — Path to 10/10

> Companion to the review of `quantum__3_.zip`. Current state: **7/10** —
> excellent engineering everywhere except the quantum layer, which currently
> doesn't run any quantum code while the pitch deck says it does. This
> document lists everything needed to close that gap and polish the rest,
> ordered by how much each item actually moves the score.

---

## How to read this document

Each item has:

- **What's wrong today** — the specific, verifiable problem
- **What to change** — the concrete fix
- **Why it matters** — what it costs you if left as-is
- **Effort** — rough time estimate for a solo dev in the remaining hackathon window

Items are grouped into four tiers. **Tier 0 is the only tier that actually
blocks a 10/10** — everything else is real, worthwhile polish, but a judge
who catches Tier 0 unaddressed will discount everything else regardless of
how good it is.

---

## Tier 0 — Blocks 10/10 entirely (fix this first, fix this fully)

### 0.1 No Qiskit code runs anywhere, despite `requirements.txt` and the pitch deck claiming it does

**What's wrong today:**
`app/services/qaoa_solver.py` contains zero imports of `qiskit`,
`qiskit_aer`, or `qiskit_algorithms`. A grep across the entire backend for
`qiskit` (case-insensitive) returns nothing. What actually runs is:
- exhaustive bitstring enumeration for ≤16 variables, or
- NumPy-based simulated annealing for 17–24 variables.

Meanwhile:
- `requirements.txt` lists `qiskit>=2.0.0`, `qiskit-aer>=0.17.0`,
  `qiskit-algorithms>=0.4.0`, `qiskit-optimization>=0.7.0` as if they're used.
- `pre_hackathon_presentation.md` states, verbatim: *"QAOA explores multiple
  routing combinations and searches for routes with lower overall cost"* and
  *"the prototype runs on a Qiskit simulator for small problem instances."*
  Neither sentence is true of the shipped code.
- `DEVIATIONS.md` is honest about this internally, but that honesty doesn't
  reach the judge-facing deck.

**What to change — pick exactly one, do it completely:**

**Option A (do this if you have ≥4–6 hours left): Make QAOA actually run.**
The QUBO is already correctly built (`qubo.py` — assignment-variable
encoding, correct penalty terms). The fix is scoped to
`_run_single_qaoa()` in `qaoa_solver.py`:

1. Pin exact working versions instead of loose `>=` ranges — the
   `PauliEvolutionGate` incompatibility `DEVIATIONS.md` describes is a
   known interaction between `qiskit-algorithms` 0.4.0's `QAOA` class and
   newer `qiskit` releases. Try pinning `qiskit==1.1.0` /
   `qiskit-algorithms==0.3.0` / `qiskit-aer==0.14.2` (a combination from
   before the breaking change) in a clean virtualenv before assuming a
   deeper incompatibility.
2. If that combination still fails, fall back to `qiskit_optimization`'s
   `MinimumEigenOptimizer` wrapping `QAOA` directly (bypassing whatever layer
   is raising `PauliEvolutionGate` errors) — this is a more standard, better-
   tested code path than hand-rolling the QAOA circuit.
3. Even `p=1`, even on a single tiny instance (4 customers, 2 vehicles, 8
   qubits) with a 30-second runtime is enough — the goal is "a real quantum
   circuit executes and returns a real sampled bitstring," not performance.
4. Keep the current SA/exhaustive path as the fallback it already resembles
   — if real QAOA raises for any reason at runtime, fall back to SA
   automatically and set a `method: "sa_fallback"` field so the honesty is
   structural, not just documented.

**Option B (do this if you have <4 hours left, or A genuinely fails):
Reframe honestly, everywhere, consistently.**
1. Rewrite every quantum-related sentence in `pre_hackathon_presentation.md`
   to match `DEVIATIONS.md`'s own honest framing. Specifically:
   - Replace *"QAOA explores multiple routing combinations..."* with
     something like: *"We formulated the CVRP as a QUBO — the same
     mathematical object QAOA optimizes — and solved it via quantum-inspired
     simulated annealing after hitting a Qiskit version incompatibility we
     couldn't resolve in the time available. The QUBO formulation is the
     quantum-computing contribution; the circuit execution layer is the
     documented next step."**
   - Remove or rewrite *"the prototype runs on a Qiskit simulator"* — it
     doesn't.
   - Rename `method: "simulated_annealing"` in the API response so the
     frontend can display "Solved via QUBO + Simulated Annealing" instead of
     implying QAOA ran, if the UI currently implies otherwise anywhere.
2. Consider renaming `qaoa_solver.py` → `qubo_solver.py` (or similar) so the
   filename itself doesn't misrepresent what's inside it. Small change, but
   it removes a discoverable inconsistency a judge reading the repo would
   otherwise flag immediately.
3. Say this out loud, unprompted, early in the live demo — "we'll be upfront
   that our quantum layer currently uses simulated annealing on the QUBO
   rather than a live QAOA circuit, here's why, here's what real QAOA would
   need" is a stronger, more credible position than waiting to be asked.

**Why it matters:** this is a quantum-computing hackathon. A project that
claims to run QAOA but doesn't, when the code is public and readable, is the
single most damaging thing a judge can discover — it recasts every other
genuinely good decision in the codebase as suspect. Fixed either way (A or
B), it becomes a *strength* — either "we got real QAOA working despite a
known package issue" or "we were rigorous enough to catch and honestly
disclose our own shortcut." Left as-is, it's a liability no amount of
polish elsewhere offsets.

**Effort:** Option A: 4–6 hours (uncertain — depends on whether a working
Qiskit version combination exists for your exact CVRP QUBO shape). Option B:
1–2 hours (mechanical, low-risk).

---

### 0.2 `runs` field says `5`, but the solver actually does 6 restarts

**What's wrong today:** `qaoa_solver.py`'s docstring and `N_RUNS = 5` config
constant say 5 runs; `DEVIATIONS.md` says *"SA internally performs
`N_RUNS × 2 = 6` restarts."* The `/api/quantum` and `/api/benchmark`
responses report `runs: 5`. A judge who reads both the code comment and the
API output side-by-side will notice the mismatch immediately — it's a small
bug, but small, easily-spotted bugs undermine confidence in the parts of the
pipeline a judge *can't* easily verify (like the QUBO math itself).

**What to change:** either report the true restart count (`runs: 6`) in the
API response, or change the internal loop to actually do 5 restarts instead
of `N_RUNS × 2`. Pick whichever is true and make the number, the docstring,
and the API response all agree.

**Why it matters:** costs nothing to fix, costs credibility to leave.

**Effort:** 15 minutes.

---

## Tier 1 — High-value, directly demo-visible

### 1.1 Zero automated tests exist

**What's wrong today:** both `backend_v2_part3.md` §28 and
`frontend_v2_part3.md` §31 specify detailed test suites — tie-case handling,
infeasible-after-repair short-circuiting, partial-state rendering, missing-
classical-data guards. None of it was implemented. `find` across the whole
repo turns up only two CSV fixture files (`test_large.csv`,
`test_small.csv`), no `test_*.py`, no `.test.jsx`/`.spec.jsx`.

**What to change — priority order if time is short, do these four first:**
1. `test_decision_engine.py`: the tie case, the infeasible-quantum case, and
   the missing-classical-data case — all three code paths already exist in
   `decision_engine.py`'s `decide()` function and are the highest-risk paths
   to have silently break right before a demo.
2. `test_qubo.py`: assert `variable_count(n_customers, n_vehicles) ==
   n_customers * n_vehicles` and that the constraint terms
   (`H_assign`, `H_capacity`) actually penalize a known-infeasible assignment
   more than a known-feasible one — a cheap, high-value sanity check on the
   core deliverable.
3. One `TestClient`-based integration test replicating exactly the smoke
   test already run manually for this review (upload → classical → quantum →
   benchmark → analytics → fleet, asserting 200 status and expected keys at
   each step) — turns a one-off manual check into a permanent regression
   guard.
4. One frontend test for `BenchmarkPanel`'s tie-rendering and infeasible-
   rendering cases (Part 3 §31.2) — the two states most likely to be hit
   live with a small demo dataset and least likely to have been manually
   clicked through during development.

**Why it matters:** the Decision Engine is the project's centerpiece. If it
silently breaks on a tie or an edge case during the live demo — with no test
having ever exercised that path — there's no safety net. Judges also
specifically credit "testing strategy" as an engineering-maturity signal;
right now the docs promise it and the repo doesn't deliver it, which is a
worse look than not having promised it at all.

**Effort:** 2–3 hours for the four items above; full coverage per the
Part 3 test plans would be a full day and isn't necessary for a 10/10 — these
four are the ones that actually protect the demo.

---

### 1.2 Runtime framing undercuts the Decision Engine's own narrative

**What's wrong today:** in the smoke test run for this review, OR-Tools took
2.0s (its default search time budget) while the SA-based "quantum" solve took
0.14s. The Decision Engine's `_explain()` function is written assuming
quantum is usually *slower* ("the extra runtime is accepted given the
distance improvement") — a reasonable assumption for real QAOA on a real
quantum backend, but backwards for the current SA implementation, which is
just fast NumPy math.

**What to change:** either (a) give OR-Tools a shorter, fixed time budget so
its runtime is a fair apples-to-apples comparison rather than an artifact of
its default search-time parameter, or (b) if keeping OR-Tools' current
budget is intentional (more search time = better routes), have
`_explain()`'s wording account for both directions cleanly — it already
has a `q_rt > c_rt` branch and an else branch, so check that the else
branch's wording ("also faster") doesn't read strangely given how often it
now fires with SA in place of real QAOA.

**Why it matters:** small, but the Decision Engine's whole value proposition
is a *credible, honest* explanation. If the "runtime tradeoff" framing
doesn't match what's actually happening for most of your demo datasets, a
sharp judge doing the mental math will notice the story doesn't quite line
up with the numbers on screen.

**Effort:** 30 minutes.

---

### 1.3 `DEVIATIONS.md` overclaims what `analytics.py` actually computes

**What's wrong today:** `DEVIATIONS.md` item 8 describes the new
`/api/analytics` endpoint as providing *"per-route analytics (load %, fuel
per route, CO₂ per route)."* The actual `analytics.py` code is more
conservative and correct than this — it deliberately returns fleet-level
aggregates only (`vehicles_used`, `average_utilization_pct`,
`average_route_km`), matching the corrected spec's own reasoning (a single
blended fuel rate can't honestly be split per-vehicle). The code is right;
the changelog describing it is wrong.

**What to change:** correct `DEVIATIONS.md` item 8's description to match
what `analytics.py` actually returns (fleet/routing aggregates, not
per-route fuel/CO₂ splits).

**Why it matters:** `DEVIATIONS.md` is clearly meant to be read by judges as
evidence of rigor — that only works if it's accurate. An overclaiming
changelog entry is a smaller version of the same problem as Tier 0.1: a
document a judge can check against the code, that doesn't match the code.

**Effort:** 10 minutes.

---

## Tier 2 — Solid polish, meaningfully raises perceived quality

### 2.1 Pin exact dependency versions, not loose ranges

**What's wrong today:** `requirements.txt` uses `>=` for every package
(`fastapi>=0.111.0`, `qiskit>=2.0.0`, etc.). This is exactly the kind of
environment drift that caused the `PauliEvolutionGate` incompatibility in
the first place (per `DEVIATIONS.md`'s own explanation) — a loose range lets
`pip install` silently pull in a newer, incompatible release on a fresh
machine or CI run.

**What to change:** run `pip freeze` against your actual working environment
and commit exact-pinned versions (`fastapi==0.111.0`, etc.) once Tier 0.1 is
resolved either way. If you're keeping the SA fallback, still pin so the
demo machine can't silently drift.

**Why it matters:** protects the demo from "it worked yesterday" failures,
and directly prevents a recurrence of the exact bug that caused the Tier 0
issue.

**Effort:** 20 minutes.

---

### 2.2 Presentation deck needs a full pass after Tier 0 is resolved

**What's wrong today:** beyond the specific QAOA-claim sentences flagged in
0.1, the deck should be read start-to-finish once Tier 0 is fixed, checking
every other slide for claims that assume real QAOA execution — e.g. any
slide showing a circuit diagram, mentioning "quantum hardware roadmap," or
showing benchmark numbers with framing that implies genuine quantum
speedup/advantage language.

**What to change:** a full read-through pass, slide by slide, cross-checked
against whichever Tier 0 option was chosen.

**Why it matters:** one corrected sentence with three uncorrected ones
nearby is barely better than zero corrected sentences — a judge who
catches one wrong claim will specifically go looking for others.

**Effort:** 30–45 minutes, after Tier 0 is settled.

---

### 2.3 Add a lightweight `/api/health`-style QAOA-status field

**What's wrong today:** there's no field in `/api/quantum` or
`/api/benchmark` that plainly states, structurally (not just in docs),
whether the solve used real quantum execution or the SA fallback.

**What to change:** add a field like `"solver_backend": "qiskit_qaoa"` or
`"solver_backend": "simulated_annealing"` to the quantum result, and surface
it directly in the frontend's `BenchmarkPanel`/`DecisionEnginePanel` — e.g.
a small badge next to the winner card: "Solved via: Simulated Annealing on
QUBO." This makes the Tier 0 honesty structural and visible in the live UI,
not just something written in a markdown file a judge has to go find.

**Why it matters:** turns "we disclosed this in a doc" into "we disclosed
this on screen, live, unprompted" — a materially stronger trust signal.

**Effort:** 45 minutes (backend field + one small frontend badge component).

---

### 2.4 Clustering path (Medium/Large tiers) — confirm it's actually wired and demo-tested

**What's wrong today:** the review's smoke test only exercised the small
(6-customer) dataset. `sample_medium.csv` and `test_large.csv` exist but
weren't run through the full pipeline as part of this review — it's unclear
whether the k-means clustering path (backend_v2 §13's Medium/Large tiers) is
fully wired into `/api/quantum`'s live solve path, or only produces the
frontend's advisory notice.

**What to change:** run the medium and large sample datasets through the
full pipeline (`upload → classical → quantum → benchmark → analytics`)
before the demo, exactly like the smoke test in this review, and confirm the
clustering path actually executes multiple per-cluster QAOA/SA solves rather
than silently falling back to NN+2opt for the whole oversized dataset.

**Why it matters:** if a judge asks to see it work on a "bigger" dataset live
and it silently degrades to the plain fallback path instead of the clustered
quantum path the deck describes, that's a second, avoidable version of the
Tier 0 problem.

**Effort:** 30–60 minutes of manual verification; more if clustering wiring
itself is incomplete.

---

## Tier 3 — Nice-to-have, only if everything above is done

### 3.1 A real per-vehicle-type emissions model

Referenced as legitimate future work in both `backend_v2.md` §16/§21 and
`frontend_v2.md` §19/§21 — moving from one blended fuel rate to a per-
vehicle-type rate applied per-route would unlock genuinely new metrics
(a real "Green Score," a real per-vehicle Fleet Dashboard) rather than
restating distance in different units. Meaningful, but scoped as multi-hour
backend work with corresponding frontend changes — only attempt this if
Tiers 0–2 are fully done with time to spare.

### 3.2 CI pipeline running the Tier 1.1 tests on every commit

Even a minimal GitHub Actions workflow running `pytest` on push would turn
the new tests from "tests that exist" into "tests that are actually
enforced" — a small additional signal of engineering maturity, but only
worth it once the tests themselves exist.

### 3.3 A second, curated "quantum wins" dataset used deliberately in the demo

`quantum_wins.csv` already exists in the repo, suggesting this was
considered. Confirm it's actually used live in the demo script (not just
present in the repo) — running it back-to-back with a dataset where
classical wins is a stronger, more credible demo than only showing the case
where quantum wins, since it lets the honest "sometimes classical wins and
here's why" framing (already built into `SustainabilitySummary.jsx` per
Deviation #11) actually get shown rather than just theoretically supported.

---

## Summary — what actually separates 7/10 from 10/10

Everything in Tier 0 is really one problem wearing two faces: **the gap
between what the code does and what the docs/deck claim it does.** Close
that gap — either by making the quantum layer real, or by making every
document and every screen say plainly that it isn't yet — and the rest of
this project (the QUBO formulation, the Decision Engine, the mixed-fleet
model, the honest "classical won and here's why" framing, the clean
corrected architecture across three documentation revisions) is already
strong enough to be a standout submission. Tier 1's testing gap is the
second-most-important item, since it's the difference between "this worked
when I tried it" and "this is protected against breaking live." Tiers 2–3
are genuine value-adds, but they're polish on a foundation — get the
foundation honest and tested first.
