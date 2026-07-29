# API Contract

This document freezes the API contract for GreenRoute V7.

### `GET /api/health`
- **Purpose:** Check if the backend is running.
- **Input JSON:** None
- **Output JSON:** `{"status": "ok", "version": "1.0"}`
- **Possible Errors:** 500 Internal Server Error

### `POST /api/upload`
- **Purpose:** Upload a CSV dataset containing depot and customer coordinates/demands.
- **Input Form-Data:** `file` (CSV)
- **Output JSON:** `{"message": "Dataset processed", "customers": 10, "depot": {"lat": 40.7128, "lng": -74.0060}}`
- **Possible Errors:** 400 Invalid CSV format.

### `POST /api/classical`
- **Purpose:** Run the OR-Tools classical CVRP solver on the uploaded dataset.
- **Input JSON:** None (uses state from `/upload`)
- **Output JSON:** See `docs/sample_response.json`
- **Possible Errors:** 400 No dataset uploaded, 422 Solver error.

### `POST /api/quantum`
- **Purpose:** Run the Quantum QAOA/VQE solver on the uploaded dataset.
- **Input JSON:** None
- **Output JSON:** See `docs/sample_response.json`
- **Possible Errors:** 400 No dataset uploaded, 500 Quantum backend timeout.

### `GET /api/compare`
- **Purpose:** Retrieve the side-by-side comparison of classical vs quantum results.
- **Input JSON:** None
- **Output JSON:** 
  ```json
  {
    "classical": { "distance_km": 120, "runtime_s": 0.5, "co2_kg": 15 },
    "quantum": { "distance_km": 125, "runtime_s": 5.0, "co2_kg": 16 }
  }
  ```
- **Possible Errors:** 400 Solvers have not been executed yet.

### `GET /api/fleet`
- **Purpose:** Get the current fleet configuration.
- **Input JSON:** None
- **Output JSON:** `{"vehicles": [{"id": 1, "capacity": 100}]}`
- **Possible Errors:** None.

### `GET /api/benchmark`
- **Purpose:** Run or retrieve automated benchmarking metrics.
- **Input JSON:** None
- **Output JSON:** `{"metrics": [...]}`

### `GET /api/analytics`
- **Purpose:** Retrieve system-wide analytics over time.
- **Input JSON:** None
- **Output JSON:** `{"total_runs": 10, "average_improvement": "5%"}`
