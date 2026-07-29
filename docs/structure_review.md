# Repository Structure Review

Overall, the repository has a good foundational structure (separating `frontend` and `backend`). However, to enhance maintainability for a collaborative team, the following organizational improvements are recommended. **(No code changes required immediately)**

## Current vs Recommended Structure

```text
quantum/
├── backend/            # Good: Backend code isolated
├── frontend/           # Good: Frontend code isolated
├── docs/               # Recommended: Centralized documentation (You are here)
├── tests/              # Note: Currently tests are inside backend/tests. Moving them to root or maintaining separate test suites for frontend/backend is ideal.
├── scripts/            # Recommended: Put utility scripts (like scratch_proof.py) here
└── data/               # Recommended: Put sample_medium.csv, sample_small.csv here
```

## Recommendations

1. **Centralize Documentation:** Ensure all architectural, API, and onboarding documentation is kept inside the `docs/` folder to prevent root directory clutter.
2. **Dedicated Scripts Folder:** Move scratchpad scripts (e.g., `scratch_proof.py`, `scratch_van_bug.py`, `scratch_api_trace.py`) into a `scripts/` or `experiments/` directory. They clutter the root backend directory.
3. **Data Folder:** Create a `data/` or `samples/` directory for test CSVs (`sample_small.csv`, `sample_medium.csv`) rather than leaving them in the root.
4. **Environment Templates:** Create `.env.example` in both `frontend/` and `backend/` to guide new developers on required environment variables.
