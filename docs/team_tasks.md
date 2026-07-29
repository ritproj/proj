# Team Tasks Breakdown

This document splits the upcoming workload among three team members.

## Member 1: Backend & Integration
- Maintain and scale the FastAPI backend.
- Integrate advanced Redis state management to replace in-memory state.
- Optimize the OR-Tools classical solver execution time.
- Ensure API inputs and outputs strictly follow `docs/api_contract.md`.
- Handle CI/CD backend deployment (e.g., Dockerization).

## Member 2: Frontend & UI
- Build and polish the React application based on the provided API contract.
- Implement the interactive Map component to render vehicle paths.
- Create dynamic charts for the `/api/compare` and `/api/analytics` data.
- Ensure responsive UI design for desktop and mobile.
- Use `docs/sample_response.json` to build UI without waiting for backend changes.

## Member 3: Documentation & Testing
- Expand Pytest test coverage (`backend/tests/`) for all edge cases.
- Write frontend unit tests (e.g., Jest / React Testing Library).
- Keep `README.md`, `architecture.md`, and `CONTRIBUTING.md` up to date.
- Prepare final project presentation and demo scenarios.
- Monitor GitHub Issues and coordinate code reviews.
