# backend-prototype.md

# GreenRoute Prototype Backend
## QT-6.22 – Quantum Assisted Capacitated Vehicle Routing

Version : MVP v1.2 (updated — vehicle type labels aligned with frontend)

---

# Objective

Build a backend capable of

- Reading customer data
- Creating a CVRP instance
- Solving using OR-Tools
- Creating a QUBO formulation
- Running QAOA on a simulator
- Comparing both solutions
- Calculating fuel consumption
- Calculating CO₂ emissions

No authentication or database is required.

---

# Technology Stack

Backend

FastAPI

Language

Python 3.11+

Libraries

FastAPI

Pydantic

NumPy

Pandas

NetworkX

Google OR-Tools

Qiskit

Qiskit Optimization

Uvicorn

---

# Backend Workflow

```
CSV Upload
      │
      ▼
Read Dataset
      │
      ▼
Validate Dataset
      │
      ▼
Distance Matrix
      │
      ▼
Vehicle Configuration
      │
      ▼
──────────────┬──────────────
              │
              ▼
      Classical Solver
              │
              ▼
         OR-Tools Result
              │
──────────────┼──────────────
              │
              ▼
      QUBO Generator
              │
              ▼
          QAOA Solver
              │
              ▼
      Feasibility Repair
              │
              ▼
      Quantum Result
              │
──────────────┬──────────────
              ▼
      Fuel Calculator
              ▼
      CO₂ Calculator
              ▼
      Comparison Response
```

---

# Project Structure

```
backend/

app/

    main.py

    routes/

        upload.py

        classical.py

        quantum.py

        compare.py

    services/

        dataset.py

        distance.py

        ortools_solver.py

        qubo.py

        qaoa_solver.py

        repair.py

        emission.py

    models/

        vehicle.py

        customer.py

        depot.py

    utils/

        helpers.py

requirements.txt
```

---

# Step 1

CSV Upload

Input

```
Customer_ID

Latitude

Longitude

Demand
```

Example

| ID | Lat | Lon | Demand |
|----|------|------|---------|
|1|11.01|76.95|12|
|2|11.03|76.96|15|

Validation

Required columns

No missing values

Demand > 0

Latitude valid

Longitude valid

Output

Python List

```
Customer Objects
```

---

# Step 1a (NEW)

Depot Definition

The CSV only contains customers. The depot must be defined separately since every route starts and ends there.

Options (pick one for MVP)

```
Option A: Fixed depot coordinates in config (e.g. depot.json)

Option B: First row of CSV flagged as depot (Customer_ID = 0)
```

Recommended for MVP

```
Option A – simplest, avoids ambiguity in CSV parsing
```

Depot Object

```
depot_id = 0

latitude

longitude
```

Depot is always index 0 in the distance matrix and always the start/end node of every vehicle route.

---

# Step 2

Vehicle Configuration

Receive

```
Vehicle Count

Vehicle Capacity

Vehicle Type
```

Example

```
3

50

Van
```

Store

```
Vehicle Object
```

Vehicle Type → Fuel Rate Mapping (UPDATED — aligned with frontend)

Vehicle Type is collected on the frontend but was previously unused. It now feeds the fuel calculator (see Step 7).

The frontend's `Upload.jsx` vehicle-type dropdown offers `['Van', 'Truck', 'Bike', 'Electric Van']`. The mapping below has been aligned to those exact label strings so no option falls through to an undefined fuel rate.

```
Van          → 0.11 L/km
Truck        → 0.18 L/km
Bike         → 0.03 L/km
Electric Van → 0.00 L/km (uses energy kWh/km instead, optional stretch)
```

Implementation note: keep this mapping as a single shared constant (e.g. `VEHICLE_FUEL_RATES` in `emission.py`) and treat an unrecognized Vehicle Type as a validation error at upload/config time rather than silently defaulting — this prevents any future frontend label drift from producing an undefined fuel rate.

---

# Step 3

Distance Matrix

Input

Customer Coordinates + Depot Coordinate

Use

Euclidean Distance

(or Haversine)

Output

```
(N+1) x (N+1) Matrix, index 0 = depot
```

Example

```
0  2  5

2  0  3

5  3  0
```

---

# Step 4

Classical Optimization

Library

Google OR-Tools

Input

Distance Matrix

Demand

Capacity

Vehicles

Depot Index (0)

Output

```
Vehicle 1

Depot

3

6

7

Depot
```

Also Return

Distance

Vehicle Load

Execution Time

---

# Step 5

Generate QUBO (EXPANDED — this is the core deliverable)

## 5.1 Problem Scope for MVP

Full CVRP QUBOs scale roughly as O(N² × K) binary variables (N = customers, K = vehicles). On a local Aer simulator this is only tractable for small instances.

```
MVP demo limit: 4–8 customers, 2–3 vehicles

Larger uploaded datasets: cluster first (k-means by location),
then solve one small QUBO per cluster
```

This limit should be stated explicitly in the demo/report — it is expected and normal for NISQ-era QAOA, not a flaw.

## 5.2 Decision Variables

```
x[i, j, k] = 1  if vehicle k travels directly from node i to node j
x[i, j, k] = 0  otherwise

i, j ∈ {0, 1, ..., N}   (0 = depot)
k ∈ {1, ..., K}         (vehicle index)
```

## 5.3 Objective Function

Minimize total distance:

```
H_distance = Σ_k Σ_i Σ_j  d(i,j) * x[i,j,k]
```

## 5.4 Constraint Terms (as penalty additions)

**Each customer visited exactly once**

```
H_visit = Σ_i ( 1 − Σ_k Σ_j x[i,j,k] )²
```

**Each vehicle departs and returns to depot exactly once**

```
H_depot = Σ_k ( Σ_j x[0,j,k] − 1 )²  +  Σ_k ( Σ_i x[i,0,k] − 1 )²
```

**Capacity constraint** (per vehicle, sum of demand on assigned nodes ≤ capacity)

```
H_capacity = Σ_k ( Σ_i demand[i] * y[i,k] − Q_k )²   [with slack variables]
```

**Subtour elimination** (prevents disconnected loops not touching the depot — a common failure mode in naive CVRP QUBOs)

```
H_subtour = MTZ-style ordering constraint per vehicle
            (u_i − u_j + N * x[i,j,k] ≤ N − 1)
```

## 5.5 Combined QUBO

```
H = H_distance
  + λ1 * H_visit
  + λ2 * H_depot
  + λ3 * H_capacity
  + λ4 * H_subtour
```

Penalty weights (λ1–λ4) are tuned so constraint violations always cost more than any possible distance saving. Start with λ = 2× max edge weight and tune empirically.

Output

```
QUBO Matrix (Q), built via Qiskit Optimization's QuadraticProgram → QUBO converter
```

---

# Step 6

Quantum Optimization (EXPANDED)

Use

Qiskit

Algorithm

QAOA

## 6.1 Configuration

```
Circuit layers (p): 2–3 (start low, increase if time allows)

Classical optimizer: COBYLA (robust, gradient-free) or SPSA

Max iterations: 100–200

Backend: Qiskit Aer simulator (AerSimulator / StatevectorSimulator)

Primitive: Qiskit Sampler
```

Run

Local Simulator

(No IBM Quantum Account required)

Input

QUBO

Output

Optimized Route (raw bitstring)

Execution Time

Objective Value

## 6.2 Feasibility Repair (NEW — required step)

QAOA sampling frequently returns bitstrings that violate one or more constraints (customer visited twice, capacity exceeded, disconnected subtour). A repair/fallback step is required so the demo does not break live.

```
1. Decode bitstring → candidate routes
2. Validate against constraints
3. If infeasible:
     - Take best feasible sample from the shot distribution, OR
     - Apply greedy local repair (reassign unvisited/duplicate customers)
4. If no feasible sample found after N shots:
     - Fall back to nearest-neighbor heuristic for that instance
       (clearly labeled in UI as "fallback used")
```

This repair step is part of the deliverable — grading criteria include quantum *solution quality*, and an honest fallback path is stronger than a demo that silently fails.

## 6.3 Benchmarking Methodology (NEW)

QAOA is stochastic — a single run is not a valid comparison point.

```
Run QAOA 5–10 times per instance

Report: mean, best, and variance of objective value

Compare best/mean vs OR-Tools optimum → report optimality gap (%)

Report mean execution time (simulator) vs OR-Tools execution time
```

---

# Step 7

Fuel Calculator (UPDATED — now uses Vehicle Type)

Formula

```
Fuel = Distance × Fuel Rate(Vehicle Type)
```

Example

Distance

30 km

Vehicle Type

Van (rate 0.11)

Fuel

3.3 L

Note: `Fuel Rate(Vehicle Type)` looks up the exact label string sent by the frontend (`Van`, `Truck`, `Bike`, or `Electric Van`) in the `VEHICLE_FUEL_RATES` mapping from Step 2 — no separate translation layer is needed as long as both sides use the same strings.

---

# Step 8

CO₂ Calculator

Formula

```
CO₂

=

Fuel

×

Emission Factor
```

Example

Petrol

2.31 kg/L

Result

```
3.3 × 2.31

=

7.62 kg
```

## Step 8a (NEW) — Sustainability Summary

In addition to raw values, compute relative savings for the comparison response and the report:

```
distance_saved_pct = (classical_distance − quantum_distance) / classical_distance × 100
fuel_saved_pct     = (classical_fuel − quantum_fuel) / classical_fuel × 100
co2_saved_pct      = (classical_co2 − quantum_co2) / classical_co2 × 100
```

---

# API Endpoints

## Upload Dataset

POST

```
/api/upload
```

Response

```
Dataset Loaded
```

---

## Classical Optimization

POST

```
/api/classical
```

Returns

```
Routes

Distance

Runtime
```

---

## Quantum Optimization

POST

```
/api/quantum
```

Returns

```
Routes

Objective

Runtime

Feasible (bool)

Fallback_used (bool)
```

---

## Comparison

GET

```
/api/compare
```

Returns

```
Distance

Fuel

CO₂

Runtime

Savings (%)
```

---

# Response Format (UPDATED)

```json
{
    "classical": {
        "distance": 31.2,
        "fuel": 3.5,
        "co2": 8.1,
        "runtime_sec": 0.8
    },

    "quantum": {
        "distance": 29.8,
        "fuel": 3.3,
        "co2": 7.6,
        "runtime_sec": 4.2,
        "feasible": true,
        "fallback_used": false,
        "objective_mean": 30.4,
        "objective_best": 29.8,
        "runs": 8
    },

    "savings": {
        "distance_pct": 4.5,
        "fuel_pct": 5.7,
        "co2_pct": 6.2
    }
}
```

---

# Backend Modules

dataset.py

Reads CSV

distance.py

Creates Distance Matrix (includes depot)

ortools_solver.py

Runs Classical Solver

qubo.py

Creates QUBO (variables, constraints, penalty terms)

qaoa_solver.py

Runs Quantum Algorithm, multiple runs for benchmarking

repair.py

Decodes bitstrings, validates feasibility, applies repair/fallback

emission.py

Fuel (vehicle-type aware)

CO₂

Savings %

---

# Development Order

## Phase 1

CSV Upload

Depot Definition

Validation

Distance Matrix

---

## Phase 2

Integrate OR-Tools

Generate Routes

Return Distance

---

## Phase 3

Generate QUBO (variables, constraints, penalty terms)

Run QAOA (multiple runs)

Feasibility repair / fallback

Return Quantum Route

---

## Phase 4

Fuel (vehicle-type aware)

CO₂

Savings %

Comparison

---

## Phase 5 (NEW)

Benchmarking across multiple QAOA runs

Optimality gap vs OR-Tools

Prepare performance comparison report

---

# Testing

Test CSV Upload

Test Depot Handling

Test Distance Matrix

Test OR-Tools

Test QUBO construction (constraint terms individually)

Test QAOA (feasible + infeasible sample cases)

Test Feasibility Repair / Fallback path

Test API Response

Test Vehicle Type → Fuel Rate mapping for all four frontend options (`Van`, `Truck`, `Bike`, `Electric Van`), including a rejection/validation-error test for any unrecognized label

---

# Future Improvements

Multiple Depots

Time Window Constraints

Electric Vehicles (energy-based fuel model)

Traffic Data

IBM Quantum Hardware

Real GPS Integration

Dynamic Routing

Automated clustering for larger datasets

---

# MVP Checklist

✅ Upload CSV

✅ Define Depot

✅ Parse Customers

✅ Configure Vehicles (incl. type → fuel rate)

✅ Generate Distance Matrix

✅ Solve using OR-Tools

✅ Generate QUBO (formal variables + constraints)

✅ Run QAOA (multi-run, benchmarked)

✅ Feasibility repair / fallback

✅ Calculate Fuel

✅ Calculate CO₂

✅ Compare Results + Savings %

---

# Demo Workflow

1.

Upload customer CSV

↓

2.

Configure vehicles (count, capacity, type)

↓

3.

Generate distance matrix (incl. depot)

↓

4.

Run OR-Tools

↓

5.

Generate QUBO

↓

6.

Run QAOA (multiple shots/runs)

↓

7.

Repair/validate feasibility

↓

8.

Compare both solutions + savings %

↓

9.

Return results to frontend

---

# Success Criteria

The prototype is complete when

- Customer data can be uploaded.
- Depot is clearly defined and used in all routing.
- Classical routes are generated successfully.
- A QUBO model is created for the same problem, with explicit variables and constraint terms.
- QAOA runs on a simulator for a small CVRP instance, with feasibility repair/fallback handling.
- Results are benchmarked across multiple QAOA runs, not a single run.
- Fuel and CO₂ metrics are calculated using vehicle type.
- Sustainability savings (%) are calculated.
- Results are returned to the frontend for visualization.
