# GreenRoute V7

> [!NOTE]
> **GreenRoute V7** is an enterprise-grade, hybrid-engine vehicle routing and fleet optimization platform. By pairing classical operations research (Google OR-Tools) with quantum computing algorithms (Qiskit QAOA & QUBO formulations), GreenRoute V7 delivers route optimization, fuel consumption reduction, and CO2 emissions tracking.

---

## Introduction

GreenRoute V7 is a next-generation logistics and route optimization application built to address the increasing complexity of urban freight distribution and last-mile logistics. Developed as a dual-solver framework, GreenRoute V7 allows logistics operators, fleet managers, and supply chain researchers to model, solve, and compare complex Capacitated Vehicle Routing Problems (CVRP).

Traditional logistics solutions rely strictly on classical heuristics or exact mathematical solvers. While classical solvers perform exceptionally well for standard fleet operations, the exponential growth of combinatorial possibilities in large-scale logistics presents scalability boundaries. GreenRoute V7 was created to bridge classical operations research with quantum computing paradigms. By benchmarking classical Google OR-Tools against Quantum Approximate Optimization Algorithms (QAOA), GreenRoute V7 provides a state-of-the-art laboratory and production tool for evaluating quantum advantages in modern logistics.

---

## Problem Statement

Modern logistics and supply chain networks face significant operational and environmental hurdles:

1. **The Combinatorial Explosion of VRP**: The Capacitated Vehicle Routing Problem (CVRP) is NP-hard. As the number of delivery locations, customer time windows, and vehicle capacity constraints grow, the number of possible route combinations expands factorially. Finding the global minimum for route distance in real-time becomes computationally prohibitive.
2. **Vehicle Capacity Constraints**: Delivery fleets consist of heterogeneous or homogeneous vehicles with strict payload and volume limits. Overloading a vehicle leads to regulatory non-compliance and vehicle wear, while under-utilization inflates operational costs.
3. **Fuel Consumption & Environmental Impact**: Inefficient routing directly translates to increased fuel consumption, higher operational expenditures, and elevated greenhouse gas (CO2) emissions. Freight transport accounts for a significant portion of global carbon output.
4. **Solver Rigidity & Hardware Limitations**: Organizations often rely on a single solver engine. Without side-by-side benchmarking, dispatchers cannot determine whether alternative heuristic or quantum algorithms could discover shorter, greener routes.

Optimization is essential to transform chaotic, high-cost delivery networks into streamlined, energy-efficient operations.

---

## Objectives

GreenRoute V7 was engineered to achieve the following core objectives:

- **Minimize Total Fleet Distance**: Reduce overall mileage across all active fleet vehicles through optimal path selection and sequence ordering.
- **Enforce Strict Capacity Compliance**: Ensure zero capacity violations by respecting maximum load thresholds for every assigned vehicle.
- **Lower CO2 Emissions and Fuel Burn**: Calculate and track environmental metrics, providing actionable data to reduce carbon footprints.
- **Dual-Solver Benchmarking**: Provide seamless side-by-side comparison between Classical (Google OR-Tools) and Quantum (Qiskit QAOA/QUBO) solvers on identical datasets.
- **Provide Intuitive Route Visualization**: Offer a dynamic, interactive map interface displaying depot hubs, customer delivery nodes, and color-coded route geometry.
- **Deliver Actionable Analytics**: Present real-time stat cards, distance charts, runtime comparisons, and fuel consumption metrics for data-driven logistics planning.

---

## Features

GreenRoute V7 equips fleet operators with a comprehensive suite of features designed for end-to-end logistics management:

### 1. CSV Upload
- **Flexible Data Ingestion**: Upload custom customer and depot datasets via a standardized CSV interface.
- **Schema Validation**: Automatically checks required columns (`id`, `lat`, `lng`, `demand`) and verifies coordinate bounds.
- **Depot Identification**: Recognizes depot nodes and maps customer delivery locations with individual demand weights.

### 2. Fleet Configuration
- **Dynamic Fleet Sizing**: Define the total number of available delivery vehicles.
- **Custom Capacity Limits**: Set maximum load capacity per vehicle to adapt to small vans, medium trucks, or heavy freight.
- **Vehicle Profiles**: Support for homogeneous fleet modeling with configurable payload constraints.

### 3. Classical Optimization
- **Google OR-Tools Integration**: Employs industry-standard Constraint Programming and Guided Local Search algorithms.
- **Distance Matrix Generation**: Computes exact geodesic (haversine) distance matrices across all network nodes.
- **Deterministic Efficiency**: Delivers fast, highly optimal routing solutions for medium to large-scale datasets.

### 4. Quantum Optimization
- **QUBO Formulation**: Maps vehicle routing constraints and distance objectives into Quadratic Unconstrained Binary Optimization matrices.
- **QAOA Solver**: Executes Quantum Approximate Optimization Algorithm circuits using Qiskit Aer simulators or quantum hardware.
- **Hybrid Clustering & Repair**: Integrates spatial clustering (K-Means/DBSCAN) and greedy route repair mechanisms to handle hardware qubit constraints efficiently.

### 5. Route Visualization
- **Interactive Map Layer**: Built on modern web mapping libraries (Leaflet / Mapbox) to render spatial node markers and path vectors.
- **Color-Coded Vehicle Routes**: Assigns distinct visual color signatures to each vehicle's generated path.
- **Interactive Node Popups**: Displays detailed customer attributes including ID, GPS coordinates, and demand values on click.

### 6. Statistics
- **Fuel & Carbon Tracking**: Automatically calculates total fuel consumption (liters) and CO2 output (kg) using standard emission models.
- **Operational Metrics**: Displays total travel distance, total active vehicles, average load utilization, and solver execution duration.
- **Exportable Metrics**: Provides normalized structured JSON statistics for reporting and downstream integration.

### 7. Route Comparison
- **Side-by-Side Solver Benchmarking**: Enables direct visual and statistical comparison between Classical and Quantum routing outcomes.
- **Metric Highlights**: Compares distance delta (%), runtime difference (seconds), and emission savings.
- **Comparative Visual Charts**: Renders intuitive side-by-side bar charts for distance, time, and fuel consumption.

---

## Technology Stack

GreenRoute V7 leverages a modern, decoupled architecture powered by industry-leading technologies:

### Backend
- **Python 3.10+**: Core programming language for computational logic and data processing.
- **FastAPI**: High-performance, asynchronous web framework for building RESTful APIs with automatic OpenAPI documentation.
- **Uvicorn**: Lightning-fast ASGI server implementation for running Python web applications.
- **Pydantic**: Data validation and settings management using Python type annotations.

### Frontend
- **React 18**: Component-based JavaScript library for building responsive user interfaces.
- **Vite / Next.js**: Modern frontend tooling for rapid development, fast hot module replacement (HMR), and optimized production builds.
- **Leaflet / React-Leaflet**: Interactive mapping library for rendering geographical nodes and route polylines.
- **Chart.js / Recharts**: Dynamic charting libraries for rendering performance benchmarking graphs.
- **CSS / Tailwind CSS**: Flexible styling framework for responsive UI design.

### Quantum
- **Qiskit SDK**: IBM's open-source quantum computing framework for quantum circuit construction.
- **Qiskit Aer**: High-performance quantum circuit simulator for classical execution of quantum algorithms.
- **Qiskit Optimization**: Domain-specific library for formulating QUBO problems and connecting to variational quantum solvers (QAOA / VQE).

### Libraries
- **Google OR-Tools**: Enterprise operations research suite for solving vehicle routing, TSP, and constraint programming problems.
- **NumPy & Pandas**: Fundamental libraries for numerical computing, matrix operations, and CSV dataset manipulation.
- **SciPy & Scikit-learn**: Scientific computing toolkits utilized for spatial clustering, distance matrix calculations, and route repair routines.
- **Pytest**: Comprehensive testing framework for backend unit, integration, and API endpoint verification.

---

## Project Workflow

The following sequential pipeline illustrates how data flows through GreenRoute V7 from initial user input to final analytics:

```text
  +-------------------+
  |   1. Upload CSV   |
  +---------+---------+
            |
            v
  +-------------------+
  |   2. Validate     |  (Validates headers, lat/lng range, demand values)
  +---------+---------+
            |
            v
  +-------------------+
  | 3. Fleet Config   |  (Set vehicle count & capacity limits)
  +---------+---------+
            |
            v
  +-------------------+
  | 4. Distance Matrix|  (Calculate geodesic distance matrix across nodes)
  +---------+---------+
            |
            +-----------------------+
            |                       |
            v                       v
  +-------------------+   +-------------------+
  |5a. Classical Solver|  |5b. Quantum Solver |  (QUBO -> QAOA / Simulator)
  |   (OR-Tools)      |   | (Qiskit + Cluster)|
  +---------+---------+   +---------+---------+
            |                       |
            +-----------------------+
            |
            v
  +-------------------+
  | 6. Route Repair   |  (Enforce capacity & sub-tour elimination)
  +---------+---------+
            |
            v
  +-------------------+
  | 7. Visualization  |  (Render interactive color-coded routes on map)
  +---------+---------+
            |
            v
  +-------------------+
  |   8. Analytics    |  (Calculate fuel, CO2, runtime, and comparison)
  +-------------------+
```

### Detailed Workflow Stages

1. **Upload CSV**: The dispatcher uploads a CSV file containing depot and delivery node records (`id`, `lat`, `lng`, `demand`).
2. **Validate**: The backend validates CSV format, ensures the presence of at least one depot node, verifies non-negative demands, and flags coordinate anomalies.
3. **Fleet Configuration**: The user configures fleet parameters (number of active vehicles, individual capacity caps).
4. **Distance Matrix**: The system computes a symmetrical matrix of pairwise geodesic distances between all locations.
5. **Classical / Quantum Solver**:
   - *Classical Path*: OR-Tools builds a routing model, applies Guided Local Search, and extracts minimal-distance vehicle tours.
   - *Quantum Path*: Nodes are clustered into manageable sub-problems, mapped into a QUBO binary formulation, solved via Qiskit QAOA on quantum simulators, and reconstructed into tours.
6. **Route Validation & Repair**: Raw solver output undergoes validation checks to guarantee zero capacity breaches and fix any broken sub-tours.
7. **Visualization**: The frontend receives standardized route JSON and plots vehicle paths with distinct colors and interactive markers on Leaflet/Mapbox maps.
8. **Analytics**: The system computes fuel consumption, carbon emissions, total mileage, and execution timing, presenting comparative metrics on stat cards and charts.

---

## Modules

GreenRoute V7 is organized into modular components with clear separation of responsibilities:

| Module | Primary Responsibility |
| :--- | :--- |
| **Backend** | Orchestrates HTTP request pipelines, manages in-memory dataset states, generates distance matrices, and invokes optimization engines. |
| **Frontend** | Renders the interactive single-page application, manages user input forms, displays mapping layers, and renders comparative analytics. |
| **Classical Solver** | Encapsulates Google OR-Tools routing model creation, search strategies, vehicle capacity dimension setups, and route extraction. |
| **Quantum Solver** | Handles spatial node clustering, QUBO matrix generation, Qiskit QAOA circuit execution, state decoding, and heuristic route repair. |
| **API Layer** | Exposes REST endpoints (`/upload`, `/fleet`, `/classical`, `/quantum`, `/compare`, `/health`, `/analytics`), validating payloads via Pydantic schemas. |
| **Documentation** | Maintains developer guides, API specifications, architecture documentation, setup instructions, and project overviews. |
| **Testing** | Houses automated Pytest test suites validating API endpoints, solver correctness, error handling, and state management consistency. |

---

## Folder Structure

Below is the directory structure of the GreenRoute V7 repository:

```text
GreenRoute-V7/
├── backend/                  # FastAPI backend server and algorithms
│   ├── app/
│   │   ├── main.py           # Application entry point & FastAPI instance
│   │   ├── config.py         # Application configuration & environment settings
│   │   ├── routes/           # REST API endpoint handlers
│   │   │   ├── upload.py     # CSV upload & parsing route
│   │   │   ├── fleet.py      # Fleet configuration management route
│   │   │   ├── solver.py     # Classical & Quantum solver trigger routes
│   │   │   ├── compare.py    # Dual-solver comparison analytics route
│   │   │   ├── health.py     # Health check endpoint
│   │   │   └── analytics.py  # System-wide metrics route
│   │   ├── services/         # Core business logic and solver engines
│   │   │   ├── ortools_solver.py # Google OR-Tools CVRP solver engine
│   │   │   ├── qaoa_solver.py    # Quantum QUBO / QAOA solver engine
│   │   │   ├── clustering.py     # K-Means / spatial clustering for Quantum solver
│   │   │   ├── route_repair.py   # Heuristic route repair & validation engine
│   │   │   ├── distance.py       # Distance matrix generation service
│   │   │   └── emission.py       # Fuel burn and CO2 emissions calculator
│   │   ├── models/           # Pydantic data schemas & request/response models
│   │   └── utils/            # Helper functions and CSV parsing utilities
│   ├── tests/                # Pytest automated test suite
│   │   ├── test_upload.py    # CSV upload tests
│   │   ├── test_solvers.py   # Solver validation tests
│   │   └── test_api.py       # API integration tests
│   └── requirements.txt      # Python backend dependencies
├── frontend/                 # React frontend web application
│   ├── src/
│   │   ├── assets/           # Static images, icons, and map markers
│   │   ├── components/       # Reusable React UI components
│   │   │   ├── MapView.jsx   # Interactive map visualization component
│   │   │   ├── Upload.jsx    # CSV upload & drag-and-drop component
│   │   │   ├── FleetForm.jsx # Fleet sizing & capacity input controls
│   │   │   ├── StatsCard.jsx # Stat summary cards (Distance, Fuel, CO2)
│   │   │   ├── Chart.jsx     # Side-by-side comparison charts
│   │   │   └── Navbar.jsx    # Application navigation bar
│   │   ├── pages/            # Top-level page views (Dashboard, Analytics)
│   │   ├── services/         # Axios/Fetch API service client modules
│   │   ├── App.jsx           # Main React root component
│   │   └── main.jsx          # DOM entry point
│   ├── package.json          # Node.js dependencies and scripts
│   └── vite.config.js        # Vite bundler configuration
├── docs/                     # Project documentation directory
│   ├── project_overview.md   # Master project overview & guide
│   ├── architecture.md       # High-level system architecture specification
│   ├── api_contract.md       # REST API contract specification
│   └── sample_response.json  # Reference JSON payload for solver outputs
└── README.md                 # Primary project README
```

---

## Backend Overview

The backend of GreenRoute V7 is built on **FastAPI**, chosen for its high execution speed, asynchronous request handling, and automatic OpenAPI schema generation.

```text
   Client Request
        │
        ▼
  +------------+      +-------------------+      +-------------------+
  |  FastAPI   | ───► |  Route Handler    | ───► | Pydantic Schema   |
  |  App Main  |      | (app/routes/*)    |      | (app/models/*)    |
  +------------+      +-------------------+      +-------------------+
                                │
                                ▼
                      +-------------------+
                      |  Service Layer    |
                      | (app/services/*)  |
                      +---------+---------+
                                |
             ┌──────────────────┴──────────────────┐
             ▼                                     ▼
   +-------------------+                 +-------------------+
   | OR-Tools Solver   |                 | Quantum Solver    |
   | (Classical CVRP)  |                 | (QUBO / QAOA)     |
   +-------------------+                 +-------------------+
```

### Key Backend Concepts
- **Asynchronous Architecture**: Asynchronous endpoint handlers prevent non-blocking I/O operations from stalling incoming client requests.
- **In-Memory State Management**: The active dataset (depot coordinates, customer nodes, demands) and generated route states are held in application state (`request.app.state`) during active sessions, eliminating unnecessary database overhead during quick iterations.
- **Modular Service Layer**: Business logic is strictly separated from HTTP routes. Solvers, distance matrix generators, and emission calculators exist as independent service modules in `app/services/`.
- **Structured Error Handling**: Centralized exception handlers catch invalid CSV formatting, unsolvable capacity constraints, or solver timeout conditions, returning meaningful HTTP error responses.

---

## Frontend Overview

The frontend is a single-page application built with **React** and bundled via **Vite**. It delivers a clean dashboard for configuring fleet parameters, triggering solver runs, inspecting route maps, and evaluating environmental impacts.

```text
  +-----------------------------------------------------------------+
  |                          Header / Navbar                        |
  +--------------------------------+--------------------------------+
  |        Control Panel           |         Map View               |
  |  - CSV File Drag & Drop        |  - Leaflet / Mapbox Map        |
  |  - Vehicle Count & Capacity    |  - Depot & Customer Markers    |
  |  - Solve Buttons (Class/Quant) |  - Color-Coded Polylines       |
  +--------------------------------+--------------------------------+
  |                     Analytics & Stat Cards                      |
  |  - Total Distance | Active Vehicles | Fuel Burn | CO2 Output    |
  |  - Side-by-Side Solver Comparison Bar Charts                    |
  +-----------------------------------------------------------------+
```

### Key Frontend Components
- **`Upload.jsx`**: Handles file selection, drag-and-drop actions, CSV parsing previews, and upload status feedback.
- **`FleetForm.jsx`**: Provides interactive input controls allowing users to adjust vehicle counts and load capacity limits dynamically.
- **`MapView.jsx`**: Renders an interactive map centered automatically on the depot location. Plots delivery nodes with customized markers and draws color-coded polyline paths for each vehicle route.
- **`StatsCard.jsx`**: Displays summary statistics cards showing total travel distance (km), fuel consumed (liters), carbon emissions (kg CO2), and solver execution time (seconds).
- **`Chart.jsx`**: Displays comparative bar charts using Chart.js/Recharts to highlight differences between Classical and Quantum routing performance.

---

## Quantum Solver Overview

The Quantum Solver in GreenRoute V7 explores how variational quantum algorithms can address NP-hard logistics problems. To overcome hardware qubit count limitations on current noisy intermediate-scale quantum (NISQ) systems, the solver uses a hybrid decomposition strategy:

### 1. Clustering
- Large customer node sets are partitioned into spatial clusters using K-Means or DBSCAN algorithms.
- Each cluster is assigned to an available vehicle based on capacity bounds, reducing the effective node count per quantum optimization pass to a size manageable by quantum simulators (such as 5 to 15 nodes per cluster).

### 2. QUBO Formulation
- The Capacitated Vehicle Routing Problem within each cluster is formulated as a Quadratic Unconstrained Binary Optimization (QUBO) problem.
- Binary decision variables represent whether a vehicle transitions directly from an origin node to a destination node.
- Distance minimization is mapped into the primary objective function terms.
- Constraints (such as visiting every customer node exactly once and enforcing valid arrival sequences) are incorporated as quadratic penalty terms.

### 3. QAOA Optimization
- The QUBO problem is converted into an Ising Hamiltonian operator.
- The Quantum Approximate Optimization Algorithm (QAOA) constructs parameterized quantum circuits with alternating cost and mixer Hamiltonian layers.
- The circuit is executed on Qiskit Aer simulators (or IBM Quantum hardware) across multiple classical-quantum variational optimization loops (using classical optimizers such as COBYLA or SPSA) to find the ground state bitstring corresponding to optimal route choices.

### 4. Route Repair
- Quantum measurement results yield probabilistic bitstrings that may occasionally violate strict deterministic constraints due to noise or sampling approximation.
- A heuristic Route Repair engine inspects the decoded bitstrings, removes sub-tour loops, resolves unvisited or duplicate nodes, and enforces strict vehicle capacity compliance.

### 5. Validation
- Reconstructed routes undergo final validation checks against distance, demand, and capacity limits before being formatted into standardized route output JSON.

---

## Classical Solver Overview

The Classical Solver leverages **Google OR-Tools**, an industry-standard framework for constraint programming and operations research.

```text
  1. Initialize Routing Index Manager (Nodes, Vehicles, Depot)
                            │
                            ▼
  2. Register Geodesic Distance Callback Matrix
                            │
                            ▼
  3. Add Vehicle Capacity Dimension Constraints
                            │
                            ▼
  4. Configure Search Parameters (Guided Local Search)
                            │
                            ▼
  5. Execute Solver Engine & Extract Vehicle Route Polylines
```

### Operational Steps
1. **Routing Index Manager**: Creates an index mapping between physical node indices (depot and customers) and OR-Tools internal solver variables for a specified number of vehicles.
2. **Distance Callback**: Registers a matrix evaluator function that returns geodesic distances between any two node indices.
3. **Capacity Constraints**: Adds a capacity dimension tracking cumulative demand along each vehicle's route, ensuring that total demand on any route does not exceed the vehicle's capacity threshold.
4. **Guided Local Search**: Configures first-solution heuristics (such as Path Cheapest Arc) combined with Guided Local Search metaheuristics to escape local minima and rapidly find global distance optimizations.
5. **Solution Extraction**: Iterates through assignment paths for every vehicle, building ordered node arrays, calculating route distances, and returning normalized route outputs.

---

## API Overview

Communication between the React frontend and FastAPI backend occurs over RESTful HTTP APIs with JSON payloads.

### Endpoint Summary

#### 1. Health API
- **`GET /api/health`**
- **Description**: Verifies backend server health and operational status.
- **Response**: `{"status": "ok", "version": "1.0"}`

#### 2. CSV Upload API
- **`POST /api/upload`**
- **Description**: Accepts a CSV dataset upload containing depot and customer coordinates and demands.
- **Request**: Multipart form data with key `file`.
- **Response**: Summary containing processed customer node counts and depot coordinates.

#### 3. Fleet API
- **`GET /api/fleet` | `POST /api/fleet`**
- **Description**: Retrieves or updates current vehicle fleet size and individual capacity parameters.
- **Response**: `{"vehicles": [{"id": 1, "capacity": 100}, {"id": 2, "capacity": 100}]}`

#### 4. Classical Solver API
- **`POST /api/classical`**
- **Description**: Triggers the Google OR-Tools solver on the currently active dataset and fleet configuration.
- **Response**: Normalized JSON containing per-vehicle route sequences, distance (km), fuel (L), CO2 (kg), and runtime (s).

#### 5. Quantum Solver API
- **`POST /api/quantum`**
- **Description**: Triggers the hybrid Quantum QUBO/QAOA solver pipeline on the uploaded dataset.
- **Response**: Normalized JSON with quantum route assignments, distance, fuel, CO2, and quantum execution runtime.

#### 6. Analytics API
- **`GET /api/compare` | `GET /api/analytics`**
- **Description**: Retrieves side-by-side comparative benchmarks between Classical and Quantum solver runs, including distance deltas, emission savings, and historical run statistics.

---

## Future Scope

GreenRoute V7 establishes a solid foundation for classical-quantum logistics optimization. Planned future enhancements include:

1. **Hybrid Quantum-Classical Solver**: Developing integrated solvers where quantum algorithms optimize high-level cluster partitioning while OR-Tools solves localized routing within clusters simultaneously.
2. **Live Traffic Integration**: Incorporating real-time traffic API feeds (Google Maps / OpenStreetMap APIs) to adjust distance and travel time matrices dynamically based on congestion patterns.
3. **Electric Vehicle (EV) Routing**: Extending capacity dimensions to track battery state-of-charge, energy consumption rates, and mandatory charging station stopover planning.
4. **Real-time Tracking**: Integrating IoT telemetry and real-time vehicle GPS tracking to re-optimize routes dynamically when delivery delays or road closures occur.
5. **Cloud Deployment**: Packaging backend services into Docker containers deployed on Kubernetes clusters with serverless quantum jobs connected directly to cloud-hosted quantum hardware (e.g., IBM Quantum / AWS Braket).

---

> *GreenRoute V7 Documentation — Building sustainable, quantum-ready logistics for tomorrow.*
