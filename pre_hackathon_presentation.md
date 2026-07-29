# pre_hackathon_presentation.md

# Quant-A-thon 2026
## QT-6.22
### GreenRoute
### Quantum Assisted Vehicle Routing for Green Logistics

---

# Slide 1
# Title

## GreenRoute

Quantum Assisted Vehicle Routing
for
Green Logistics

Team ID:
(Add Team ID)

Team Members

- Member 1
- Member 2
- Member 3
- Member 4

---

# Slide 2
# Problem Statement

## The Last Mile – Capacitated Vehicle Routing Problem (CVRP)

Modern logistics companies deliver thousands of packages every day.

Challenges include:

- Long delivery distances
- High fuel consumption
- Carbon emissions
- Vehicle capacity constraints
- Increasing transportation costs

Finding the best delivery routes is a complex optimization problem.

---

# Slide 3
# Why is this Difficult?

Vehicle Routing Problem (VRP)

↓

Capacitated Vehicle Routing Problem (CVRP)

Constraints

- Every customer must be visited exactly once.
- Vehicle capacity cannot be exceeded.
- Every vehicle starts and ends at the depot.
- Total distance should be minimized.

CVRP is an NP-Hard optimization problem.

As the number of customers increases, the number of possible routes grows exponentially.

---

# Slide 4
# Proposed Solution

We propose a **Hybrid Classical + Quantum Optimization System**.

Workflow

```
Customer Dataset

↓

Distance Matrix

↓

CVRP Model

↓

Classical Solver (OR-Tools)

↓

QUBO Formulation

↓

QUBO Solver (Simulated Annealing)

↓

Optimized Routes

↓

Fuel & CO₂ Analysis
```

---

# Slide 5
# System Architecture

```
CSV Upload

↓

Distance Matrix

↓

Vehicle Configuration

↓

CVRP

↓

────────────────────────

OR-Tools

↓

Classical Route

────────────────────────

QUBO

↓

Simulated Annealing (QUBO)

↓

Quantum Route

────────────────────────

↓

Comparison

↓

Dashboard
```

---

# Slide 6
# Classical Optimization

We use Google OR-Tools as the baseline.

Why OR-Tools?

- Industry standard
- Fast
- Reliable
- Produces feasible routes
- Handles capacity constraints

Output

- Optimized routes
- Distance
- Runtime

---

# Slide 7
# Quantum Optimization

The optimization problem is converted into a QUBO.

Binary Variables

```
0

or

1
```

represent routing decisions.

The CVRP is formulated as a Quadratic Unconstrained Binary Optimization (QUBO) problem.

The QUBO is solved using Simulated Annealing (SA), providing the same objective optimization without requiring Qiskit dependencies.

This approach minimizes the exact same mathematical QUBO objective function that would be targeted by a QAOA circuit, representing our core quantum-computing contribution.

---

# Slide 8
# Sustainability

After optimization we calculate

Distance

↓

Fuel Consumption

↓

Carbon Emissions

Formula

Fuel

=

Distance × Fuel Rate

CO₂

=

Fuel × Emission Factor

Goal

Reduce

- Fuel usage
- Delivery cost
- Carbon emissions

---

# Slide 9
# Technology Stack

Frontend

- React
- Tailwind CSS
- React Leaflet

Backend

- FastAPI
- Python

Optimization

- Google OR-Tools

Quantum (Formulation)

- Qiskit (QUBO mapping)

Optimization (Solver)

- NumPy / Python (Simulated Annealing)

Visualization

- Chart.js

---

# Slide 10
# Expected Output

The dashboard will display

- Delivery routes
- Vehicle utilization
- Distance travelled
- Fuel consumption
- Carbon emissions
- Classical vs Quantum comparison

Example

| Metric | Classical | Quantum |
|---------|-----------|----------|
| Distance | 32 km | 30 km |
| Fuel | 3.8 L | 3.5 L |
| CO₂ | 9.2 kg | 8.4 kg |

*(Illustrative values for demonstration.)*

---

# Slide 11
# Innovation

Our solution combines

✅ Classical Optimization

+

✅ Quantum Optimization

to build a practical hybrid logistics system.

Key Innovations

- Hybrid OR-Tools + QAOA workflow
- QUBO-based CVRP formulation
- Green logistics optimization
- Fuel and CO₂ estimation
- Interactive visualization dashboard

---

# Slide 12
# Future Scope

Future improvements include

- Real-time traffic integration
- Electric vehicle routing
- Multiple depots
- Delivery time windows
- Live GPS tracking
- Execution on IBM Quantum Hardware

---

# Slide 13
# Conclusion

GreenRoute demonstrates how hybrid quantum computing can assist classical optimization to improve delivery planning.

Benefits

- Reduced travel distance
- Lower fuel consumption
- Lower carbon emissions
- Better vehicle utilization
- Scalable hybrid architecture

---

# Slide 14
# Thank You

Thank You

Questions?