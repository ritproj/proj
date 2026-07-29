
# GreenRoute — Final Improvement List (Post-V4)

> Consolidates `path_to_10.md`, the V4 review, and the encoding/Qiskit
> clarification into one final punch list. Three buckets: what's already
> fine and shouldn't be touched, what V4 already fixed, and what's still
> genuinely required. Nothing below asks you to change an engineering
> decision — only to close specific, checkable gaps between what the
> project says and what it does.

---

## Bucket 0 — Already correct, do not change

These are sound engineering decisions and were never scored down. Listed
here explicitly so they don't get re-litigated or accidentally "fixed" into
something worse under time pressure:

- **Assignment-variable QUBO encoding (`y[i,k]`) over arc-variable
  (`x[i,j,v]`).** Standard, correct NISQ-era simplification. Keep it.
- **Simulated Annealing as the solver for the QUBO**, as a documented
  fallback when real QAOA circuit execution isn't available. Mathematically
  solving the same `x^T Q x` objective is a legitimate substitute. Keep it.
- **Nearest-neighbor + 2-opt as the quantum fallback path**, and as the
  decoder that avoids needing MTZ subtour-elimination variables. Keep it.
- **Mixed-fleet per-vehicle-type capacity model.** Correct fix over the
  original single-capacity spec. Keep it.
- **Decision Engine's normalized distance+runtime scoring**, excluding
  fuel/CO₂ as redundant linear restatements of distance. Keep it.

---

## Bucket 1 — Already fixed in V4, confirmed by testing

No action needed — verified via direct API smoke-testing, not just code
reading:

- ✅ `runs` field now correctly reports the real independent-restart count
  (`runs: 5`, matching an actual 5-iteration outer loop) instead of the
  previous mismatch against internal restarts.
- ✅ A `method` field (`"exhaustive"` / `"simulated_annealing"` /
  `"nn_fallback"`) is now threaded through `/api/quantum` → `/api/benchmark`
  → `BenchmarkTable.jsx`, rendered as a plain-language label. This is the
  structural, on-screen honesty fix — confirmed live in the UI, not just in
  a doc.
- ✅ `qaoa_solver.py`'s own docstring no longer claims QAOA circuit
  execution — now accurately says "QUBO-based CVRP solver."
- ✅ New `/api/reset` endpoint (not previously required, sensible addition
  for running multiple demo datasets without restarting the server).

---

## Bucket 2 — Still required, in priority order

### 2.1 — Align the two judge-facing artifacts with what `DEVIATIONS.md` already admits

**What's wrong:** `pre_hackathon_presentation.md` still states *"the
prototype runs on a Qiskit simulator"* and lists Qiskit/QAOA as load-bearing
tech stack. `requirements.txt` still lists `qiskit`, `qiskit-aer`,
`qiskit-algorithms`, `qiskit-optimization` as if they're used. Neither has
changed since before V4. Meanwhile `DEVIATIONS.md` — which nothing requires
a judge to open — already contains the honest explanation.

**What to change:**
- Rewrite the relevant deck slides to say what `method` field / `DEVIATIONS.md`
  already say internally: the CVRP is formulated as a QUBO, solved via
  simulated annealing after a documented Qiskit version incompatibility,
  with the QUBO formulation as the quantum-computing contribution.
- Remove the four unused Qiskit packages from `requirements.txt`, **or** —
  if you decide to make one more real attempt at Path A first (see 2.2) —
  leave them only if that attempt succeeds.
- This is a documentation-only change. Zero solver code needs to move.

**Why this is still first, even after V4's real progress:** V4 fixed the
*internal* consistency (code ↔ `method` field ↔ UI badge). This item is the
*external* consistency (code ↔ pitch deck). Both matter, and only one has
been done. A judge who reads the deck before opening the code will still
see a false claim.

**Effort:** 1–2 hours.

### 2.2 — One real, deliberate attempt at an older Qiskit version pin, if not already tried

**What's wrong:** `DEVIATIONS.md` attributes the failure specifically to
`qiskit_algorithms 0.4.0` + `qiskit 2.5.0`, described as "installed
versions" — this reads as the versions that happened to be installed, not
necessarily a deliberately-chosen older combination.

**What to change:** in a clean virtualenv, try
`qiskit==1.1.0` / `qiskit-algorithms==0.3.0` / `qiskit-aer==0.14.2` (a
combination that predates the `PauliEvolutionGate` interaction described)
against your existing QUBO → `MinimumEigenOptimizer(QAOA(...))` code path.

**Two possible outcomes, both good:**
- It works → Path A is achieved. Even `p=1` on a tiny instance is enough —
  update the `method` field to include `"qiskit_qaoa"`, update the deck to
  say real QAOA runs, done.
- It still fails → you now have a *specific, attempted, and failed* version
  combination to cite in `DEVIATIONS.md`, which is a materially stronger
  disclosure than citing only the versions you happened to have installed.
  Proceed to 2.1 with full confidence the deviation is genuinely necessary.

**Effort:** 1–2 hours, timeboxed. Do not let this expand — one clean attempt,
then move on regardless of outcome.

### 2.3 — Wire `cluster_customers()` into the live `/api/quantum` path, or stop implying it's wired

**What's wrong:** confirmed by direct testing (not just code reading) —
running `test_large.csv` (30 customers) through the live pipeline returns
`method: "nn_fallback"`, `fallback_used: true`. The k-means clustering
function in `dataset.py` is never called from the solve path. This is not
listed in `DEVIATIONS.md` as an intentional trade-off — it's simply
unfinished, and the backend_v2 docs' "Medium/Large hybrid strategy" section
describes behavior that doesn't currently exist.

**What to change — pick one:**
- **Wire it in** (preferred if time allows): in `solve_quantum()`, when
  `len(customers) > QAOA_CUSTOMER_LIMIT`, call `cluster_customers()` to
  split into groups of ≤8, run the existing QUBO/SA solve per cluster, and
  concatenate the resulting routes — instead of dropping straight to
  `_nn_result(fallback=True)`.
- **Or, if time doesn't allow:** add this as its own item in
  `DEVIATIONS.md` (it currently isn't documented at all), and make sure
  neither the deck nor the backend_v2 docs claim a clustered quantum path
  exists for medium/large datasets. Same principle as 2.1 — an honestly
  documented gap costs far less than an undocumented one a judge discovers
  by testing, which is exactly how this was found in this review.

**Effort:** wiring: 2–3 hours. Documenting-only: 15 minutes.

### 2.4 — Fix the two stale spots in `DEVIATIONS.md` itself

- **Item #4** still describes the *old* behavior ("single SA call,"
  "`runs` is reported as `1`") — the code has since genuinely improved to 5
  real independent runs. Update the entry so it doesn't undersell your own
  fixed work.
- **Item #8** still claims `/api/analytics` returns "per-route fuel/CO₂" —
  it doesn't, and correctly doesn't (a blended fleet rate can't honestly be
  split per-vehicle). The code is right; the changelog describing it isn't.

**Why this matters:** `DEVIATIONS.md` is your strongest piece of evidence of
engineering rigor — that only works if it's accurate in both directions,
not just honest about limitations but also accurate about what's already
fixed.

**Effort:** 15 minutes total.

### 2.5 — Minimum viable automated tests (unrelated to any of the above, still outstanding)

No test files exist anywhere in the repo. At minimum, before the demo:

1. `test_decision_engine.py` — tie case, infeasible-quantum case,
   missing-classical-data case.
2. `test_qubo.py` — variable count sanity, constraint-term sanity.
3. One `TestClient` integration test covering the full pipeline
   (upload → classical → quantum → benchmark → reset), asserting the
   `method` field is present and correctly reflects the solve path taken.
4. One frontend test for `BenchmarkTable`'s method-label rendering across
   all three `method` values.

**Effort:** 2–3 hours for all four.

### 2.6 — Pin exact dependency versions

Once 2.1/2.2 settle which Qiskit packages (if any) actually belong in
`requirements.txt`, pin every dependency to an exact version, not a loose
`>=` range — this is also direct prevention against a repeat of the exact
bug that started this whole conversation.

**Effort:** 20 minutes.

---

## What "done" looks like

Every item in Bucket 2 closed, specifically meaning:

- The pitch deck and `requirements.txt` say the same thing `DEVIATIONS.md`
  and the `method` field already say.
- Running a 30-customer dataset through the live demo either genuinely
  triggers a clustered quantum solve, or the deck doesn't claim it does.
- `DEVIATIONS.md` accurately describes current behavior in both directions
  — neither overclaiming nor underclaiming what's implemented.
- Four tests exist and pass.
- `requirements.txt` is fully pinned.

At that point, every remaining gap between the code and the story you tell
about it is closed — which is the actual definition of a 10/10 here: not
"more features," but "nothing a judge can catch that you didn't already
catch and disclose first."
