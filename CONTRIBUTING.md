# Contributing to GreenRoute V7

Welcome to GreenRoute! To ensure a smooth collaborative workflow, please follow these guidelines.

## Branch Strategy
We follow a standard feature-branch workflow.
- `main` - Stable, production-ready code.
- `develop` - Integration branch for features.
- `feature/<feature-name>` - For new features (e.g., `feature/quantum-solver`).
- `bugfix/<bug-name>` - For fixing bugs (e.g., `bugfix/map-rendering`).

## Commit Message Format
Use descriptive, imperative commit messages.
- `feat: Add API endpoint for benchmark`
- `fix: Resolve null pointer in OR-Tools service`
- `docs: Update architecture diagram`
- `style: Format React components`

## Pull Request Workflow
1. Create a branch from `develop`.
2. Commit your changes locally.
3. Push to your branch on GitHub.
4. Open a Pull Request (PR) against the `develop` branch.
5. Request a review from at least one team member.
6. Once approved, squash and merge into `develop`.

## Code Review Checklist
- [ ] Code follows project styling (PEP 8 for Python, Prettier for JS/TS).
- [ ] No hardcoded secrets or environment variables are pushed.
- [ ] Logic is covered by unit tests if applicable.
- [ ] New APIs are documented in `docs/api_contract.md`.

## Testing Checklist
- [ ] Ran `pytest` in the backend and all tests pass.
- [ ] Verified frontend build succeeds (`npm run build`).
- [ ] Tested end-to-end flow locally (Upload -> Solve -> View Map).

## How to Report Bugs
If you find a bug, open an Issue on GitHub with:
1. A clear, descriptive title.
2. Steps to reproduce the bug.
3. Expected behavior vs Actual behavior.
4. Error logs or screenshots.
