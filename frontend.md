# frontend-prototype.md

# GreenRoute Prototype
## QT-6.22 – Quantum Assisted Vehicle Routing

Version: MVP v1.1 (updated)

---

# Objective

Build a simple web application that allows a user to:

- Upload customer data
- Configure vehicles
- Run Classical Optimization
- Run Quantum Optimization
- Compare the results
- Visualize delivery routes
- See sustainability impact and a presentable summary

This is a prototype, so focus on functionality rather than advanced UI.

---

# Tech Stack

Framework
- React

Language
- JavaScript

Styling
- Tailwind CSS

HTTP Client
- Axios

Routing
- React Router

Map
- React Leaflet

Charts
- Chart.js

Icons
- Lucide React

---

# Application Flow

```
Landing Page
        │
        ▼
Upload Dataset
        │
        ▼
Dashboard
```

Only **3 pages** are required.

---

# Landing Page

Purpose

Introduce the project.

Layout

```
-------------------------------------

GreenRoute

Quantum Assisted
Vehicle Routing

Optimize Routes
Reduce Fuel
Reduce Carbon Emission

[ Start ]

-------------------------------------
```

Components

```
Navbar

Hero

Start Button
```

Button Action

Navigate to

```
/upload
```

---

# Upload Page

Purpose

Collect all required inputs.

Layout

```
--------------------------------

Upload CSV

Choose File

-------------------------------

Vehicle Count

Vehicle Capacity

Vehicle Type

-------------------------------

Run Optimization

--------------------------------
```

Inputs

### CSV Upload

Accept

```
.csv
```

Required Columns

```
Customer_ID

Latitude

Longitude

Demand
```

Vehicle Inputs

```
Vehicle Count

Vehicle Capacity

Vehicle Type
```

Example

```
Vehicle Count

3

Vehicle Capacity

50

Vehicle Type

Van
```

Validation

Show error if

- no file selected
- wrong format
- missing columns
- demand ≤ 0 in any row
- dataset exceeds MVP demo size (see note below)

Note (NEW)

```
QAOA runs on a local simulator, which realistically supports
only 4–8 customers / 2–3 vehicles per instance.

If the uploaded CSV has more customers than this, show a
non-blocking notice: "Dataset will be clustered for quantum
demo purposes" — do not silently fail.
```

---

# Dashboard

Purpose

Display optimization results.

Layout

```
------------------------------------------------

Statistics

------------------------------------------------

Sustainability Summary

------------------------------------------------

Map

------------------------------------------------

Comparison

------------------------------------------------
```

---

# Statistics Section

Display

```
Customers

Vehicles

Distance

Fuel

CO₂
```

Example

```
Customers

12
```

```
Vehicles

3
```

```
Distance

31 km
```

```
Fuel

3.5 L
```

```
CO₂

8.2 kg
```

---

# Sustainability Summary (NEW SECTION)

Purpose

Give judges/viewers a single headline takeaway instead of only raw numbers — this directly supports the "Sustainability Impact" and "Presentation" evaluation criteria.

Layout

```
------------------------------------------------

Quantum Route Saves

Distance   -4.5%
Fuel       -5.7%
CO₂        -6.2%

------------------------------------------------
```

Data Source

```
GET /api/compare → savings.distance_pct, savings.fuel_pct, savings.co2_pct
```

Display Rule

```
If quantum result is NOT better than classical (can happen,
QAOA is approximate): show neutral framing, e.g.
"Quantum matched classical performance on this run"
instead of a misleading negative-savings badge.
```

Optional stretch

```
Translate CO₂ saved into a relatable equivalent
e.g. "≈ 0.3 tree-days of CO₂ absorption"
(nice for the Presentation score, not required for MVP)
```

---

# Route Map

Use

```
React Leaflet
```

Display

- Depot (distinct marker/icon, always shown)
- Customers
- Vehicle Routes

Color

Depot

Black / distinct pin icon

Vehicle 1

Blue

Vehicle 2

Green

Vehicle 3

Orange

Marker Popup

```
Customer 5

Demand

15 kg
```

Depot Popup (NEW)

```
Depot

Start / End point for all vehicles
```

---

# Comparison Table

Simple table

| Metric | Classical | Quantum |
|----------|-----------|-----------|
| Distance | 32 km | 30 km |
| Fuel | 3.8 L | 3.5 L |
| CO₂ | 9.1 kg | 8.3 kg |
| Runtime | 0.8 s | 4.2 s |

Runtime row added (NEW) — makes the classical-vs-quantum tradeoff honest: quantum may win on distance/fuel/CO₂ but cost more runtime on a simulator. This is a legitimate and expected finding, not a weakness to hide.

No charts required for MVP, except the optional Sustainability Summary bar (see below).

---

# Optional Result Chart (NEW, light-weight)

Purpose

One small Chart.js bar chart comparing Classical vs Quantum across Distance / Fuel / CO₂, placed above or beside the Comparison Table. Not required, but strengthens both "Route Optimization Performance" and "Presentation" scoring for very little extra effort since Chart.js is already in the stack.

```
Simple grouped bar chart:
  X-axis: Distance, Fuel, CO2
  Series: Classical, Quantum
```

---

# Result / Error States (NEW)

The dashboard must handle non-happy-path states explicitly, since QAOA can return infeasible or fallback results.

```
State: Loading
  "Running OR-Tools..." / "Generating QUBO..." / "Running QAOA..."

State: Quantum Feasible
  Show results normally

State: Quantum Infeasible → Fallback Used
  Show quantum results with a visible badge:
  "Fallback heuristic used (QAOA did not converge to a feasible route)"

State: Backend/API Error
  Show a simple error banner + Reset button, do not crash the dashboard
```

---

# Buttons

Dashboard contains

```
Run Classical

Run Quantum

Compare

Reset
```

Loading State

```
Running OR-Tools...
```

```
Generating QUBO...
```

```
Running QAOA...
```

---

# API Calls

Upload Dataset

```
POST

/api/upload
```

Run Classical

```
POST

/api/classical
```

Run Quantum

```
POST

/api/quantum
```

Compare

```
GET

/api/compare
```

Response fields consumed (NEW)

```
quantum.feasible
quantum.fallback_used
savings.distance_pct
savings.fuel_pct
savings.co2_pct
```

---

# Folder Structure

```
frontend/

src/

    components/

        Navbar.jsx

        UploadBox.jsx

        StatsCard.jsx

        SustainabilitySummary.jsx

        RouteMap.jsx

        ComparisonTable.jsx

        ResultChart.jsx

        ErrorBanner.jsx

    pages/

        Landing.jsx

        Upload.jsx

        Dashboard.jsx

    services/

        api.js

    App.jsx

    main.jsx
```

---

# React Component Tree

```
<App>

    Navbar

    Router

        Landing

        Upload

        Dashboard

            StatsCard

            SustainabilitySummary

            RouteMap

            ComparisonTable

            ResultChart

            ErrorBanner
```

---

# State

Store

```
Uploaded Dataset

Vehicle Details

Classical Result

Quantum Result

Comparison / Savings

Feasibility / Fallback Flags

Error State
```

Simple React Context is enough.

---

# User Flow

```
Landing

↓

Upload CSV

↓

Configure Vehicles

↓

Run Classical

↓

Run Quantum

↓

Compare Results + Sustainability Summary
```

---

# MVP Features

✅ Landing Page

✅ CSV Upload

✅ Vehicle Configuration

✅ Dashboard

✅ Route Map (with depot marker)

✅ Statistics

✅ Sustainability Summary

✅ Comparison Table (incl. runtime)

✅ Infeasible / Fallback / Error states

---

# Features NOT Included

❌ Login

❌ Authentication

❌ Database

❌ User Accounts

❌ PDF Download

❌ Live Traffic

❌ GPS Tracking

❌ Notifications

❌ Multi Depot Routing

❌ Time Window Constraints

---

# Development Plan

## Day 1

- Create React project
- Install Tailwind
- Create pages
- Configure routing

## Day 2

- CSV Upload
- Vehicle Form
- Axios integration
- Dataset-size notice (clustering note)

## Day 3

- Route Map (incl. depot marker)
- Statistics
- Sustainability Summary
- Comparison Table + optional chart
- Error / infeasible / fallback states

---

# Demo Flow

1. Open GreenRoute
2. Click Start
3. Upload customer CSV
4. Enter vehicle count, capacity, and type
5. Click Run Classical
6. Click Run Quantum
7. Show optimized routes on map (depot + vehicles)
8. Show Sustainability Summary (headline savings %)
9. Compare distance, fuel, CO₂, and runtime side by side

Total demo time:
5 minutes

---

# Success Criteria

The frontend is considered complete when:

- User can upload a CSV.
- User can configure the fleet (count, capacity, type).
- Backend APIs can be called successfully.
- Optimized routes are displayed on the map, including the depot.
- Classical and Quantum results are shown side by side, including runtime.
- A clear sustainability savings summary is shown (not just raw numbers).
- Infeasible-route and fallback cases are visibly and honestly communicated, not hidden.
- The interface is clean, responsive, and easy to demonstrate.
