# Architecture Documentation

## System Architecture
GreenRoute V7 uses a decoupled frontend-backend architecture.
- **Frontend:** React application responsible for user inputs, map rendering, and displaying analytics.
- **Backend:** FastAPI application that manages dataset state in memory and routes computational requests to either the Classical or Quantum solver engines.

## Data Flow
1. User uploads a CSV via Frontend -> `POST /api/upload`.
2. Backend parses CSV, stores `depot` and `customers` in application state.
3. User triggers solve via `POST /api/classical` or `POST /api/quantum`.
4. Backend retrieves state, executes the respective solver.
5. Solver calculates distance, routes, fuel, and CO2 emissions.
6. Backend returns normalized JSON (`sample_response.json`).
7. Frontend renders routes on the map and updates stat cards.

## Frontend Flow
- **State Management:** Manages UI states (loading, errors, success).
- **Map Layer:** Renders polylines for routes and markers for depots/customers using Leaflet/Mapbox.
- **Dashboard:** Fetches `/api/compare` to display comparative bar charts.

## Backend Flow
- **Routers (`app/routes/`):** Receives HTTP requests, validates input, calls services.
- **Services (`app/services/`):** Contains the core business logic (e.g., `emission.py`, `ortools_solver.py`, `qaoa_solver.py`).
- **State Management:** In-memory state via `request.app.state` (Note: for production scaling, a Redis cache is recommended).

## Quantum Solver Flow
1. Maps the CVRP problem to a Quadratic Unconstrained Binary Optimization (QUBO) problem.
2. Connects to Qiskit Aer simulator (or real hardware).
3. Executes QAOA/VQE to find the optimal bitstring.
4. Decodes bitstring back into physical vehicle routes.

## Classical Solver Flow
1. Uses Google OR-Tools Routing Model.
2. Sets up distance callbacks, capacity dimensions, and search parameters.
3. Executes Guided Local Search to find an optimal solution.

## Folder Responsibilities
- `backend/app/routes/`: API endpoint definitions.
- `backend/app/services/`: Algorithm implementations.
- `backend/tests/`: Pytest framework.
- `frontend/src/components/`: Reusable React components.
