# 📦 Test Datasets — BQPhy CVRP Solver

All datasets use **depot: `11.0168, 76.9558` (Coimbatore city centre)**.  
Format: `Customer_ID,Latitude,Longitude,Demand`

---

## 🟢 Group 1 — Tiny (1–12 customers) — No Clustering

| # | File | Customers | Pattern | Recommended Fleet | Recommended Cap |
|---|------|-----------|---------|-------------------|-----------------|
| 01 | `01_tiny_3cust_equal.csv` | 3 | Tight cluster, equal demand=15 | Van×1 | Van=50 |
| 02 | `02_small_6cust_hexagon.csv` | 6 | Perfect hexagon, equal demand=20 | Van×3 | Van=50 |
| 03 | `03_small_8cust_octagon.csv` | 8 | Symmetric octagon, equal demand=16 | Van×4 | Van=50 |
| 04 | `04_small_10cust_linear_mixed.csv` | 10 | Linear layout, mixed demand 7–20 | Van×3 | Van=50 |
| 05 | `05_small_12cust_two_clusters.csv` | 12 | Two geographic clusters, demand=12 | Van×3 | Van=50 |

---

## 🟡 Group 2 — Medium (20–50 customers) — Approaching Limit

| # | File | Customers | Pattern | Recommended Fleet | Recommended Cap |
|---|------|-----------|---------|-------------------|-----------------|
| 06 | `06_medium_20cust_grid.csv` | 20 | Regular 4×5 grid, demand=10 | Van×5 | Van=50 |
| 07 | `07_medium_25cust_random.csv` | 25 | Random city area, mixed demand 5–25 | Van×5 | Van=60 |
| 08 | `08_medium_30cust_concentric.csv` | 30 | 3 concentric rings, demand=14 | Van×6 | Van=50 |
| 09 | `09_medium_35cust_highdemand.csv` | 35 | Sparse, high demand=40 each | Truck×10 | Truck=120 |
| 10 | `10_medium_40cust_sprawl.csv` | 40 | Gaussian sprawl, mixed demand 8–30 | Van×8 | Van=60 |
| 11 | `11_boundary_50cust_nocluster.csv` | **50** | Random — **exactly at clustering limit** | Van×10 | Van=60 |

---

## 🔴 Group 3 — Large / XL (51–100 customers) — Triggers Clustering

| # | File | Customers | Pattern | Recommended Fleet | Recommended Cap |
|---|------|-----------|---------|-------------------|-----------------|
| 12 | `12_cluster_51cust.csv` | **51** | Random — **just above limit, clustering on** | Van×10 | Van=60 |
| 13 | `13_large_60cust_4zones.csv` | 60 | 4 geographic zones, mixed demand 8–25 | Van×10 | Van=60 |
| 14 | `14_large_70cust_spiral.csv` | 70 | Spiral layout, mixed demand 5–20 | Van×10 | Van=60 |
| 15 | `15_large_80cust_city.csv` | 80 | Real city-style Gaussian, mixed demand | Van×10 | Van=60 |
| 16 | `16_large_90cust_star.csv` | 90 | Star (radial from depot), mixed demand 6–22 | Van×10 | Van=60 |
| 17 | `17_xl_100cust_random.csv` | **100** | Uniform random, mixed demand 5–30 | Van×10 | Van=60 |
| 18 | `18_xl_100cust_dense_downtown.csv` | **100** | Dense downtown Gaussian, demand 8–20 | Van×10 | Van=50 |

---

## ⚠️ Group 4 — Edge Cases

| # | File | Customers | What it Tests |
|---|------|-----------|---------------|
| 19 | `19_edge_5cust_capacity_exact.csv` | 5 | 5×10=50 demand = van capacity exactly |
| 20 | `20_edge_4cust_per_vehicle.csv` | 4 | Each customer demand=50 → needs 1 van each |
| 21 | `21_edge_6cust_same_location.csv` | 6 | All customers at same coords → zero distances |
| 22 | `22_edge_8cust_integer_demands.csv` | 8 | Integer demands (no decimal point) |
| 23 | `23_edge_10cust_mixed_demands.csv` | 10 | Extreme variance: demand ranges 1–100 |
| 24 | `24_edge_10cust_linear_street.csv` | 10 | All on same latitude (E-W street) |
| 25 | `25_edge_10cust_two_distant_clusters.csv` | 10 | Two clusters 16 km apart → forces 2 vehicles |

**For edge cases 19–25 use:** `Van×4, Van_cap=50`  
**For dataset 20:** `Van×4, Van_cap=50`  
**For dataset 23:** `Truck×5, Truck_cap=120`

---

## ⚛️ Group Q — Quantum-Optimal Datasets

These are **specifically engineered** to maximize quantum advantage. They have:
- **Symmetric geometry** → QUBO energy landscape has sharp, clear global minimum
- **Equal demands** → no trivial greedy/NN solution — every partition looks equal to classical solvers
- **Demand × K ≈ capacity exactly** → forces the solver into a hard combinatorial partition problem

| # | File | Customers | Geometry | Why Quantum Wins |
|---|------|-----------|----------|-----------------|
| Q1 | `Q1_hexagon_3veh_equal.csv` | 6 | Perfect hexagon | 3-way symmetric partition, demand=20, cap=40 |
| Q2 | `Q2_double_hexagon_4veh.csv` | 12 | Double concentric hexagon | Inner+outer ring symmetry, demand=12, cap=36 |
| Q3 | `Q3_cross_8cust_2veh.csv` | 8 | Cardinal + diagonal cross | 2-way symmetric split, demand=16, cap=64 |
| Q4 | `Q4_paired_6cust_3veh.csv` | 6 | 3 far-apart pairs | Exact pair partition, demand=25, cap=50 |
| Q5 | `Q5_balanced_4cluster_8cust.csv` | 8 | 4 balanced clusters | Each cluster fills 1 vehicle exactly |
| Q6 | `Q6_star_7cust.csv` | 7 | Star (center + 6 rim) | Non-obvious optimal grouping |
| Q7 | `Q7_grid_9cust_3x3.csv` | 9 | 3×3 grid | Multiple symmetric routes, demand=11, cap=33 |
| Q8 | `Q8_pentagon_5cust.csv` | 5 | Regular pentagon | 2-way asymmetric split — quantum finds it |
| Q9 | `Q9_octagon_capcity_tight.csv` | 8 | Regular octagon | 4 vehicles × cap=20 fits 2 nodes each exactly |
| Q10 | `Q10_large_20cust_4clusters_quantum_optimal.csv` | 20 | 4×5 perfect clusters | Largest quantum-optimal — 4 clusters, demand=15 |

### Fleet configs for Quantum-Optimal datasets:

| Dataset | Fleet | Capacity |
|---------|-------|----------|
| Q1 | Van×3 | Van=40 |
| Q2 | Van×4 | Van=36 |
| Q3 | Van×2 | Van=64 |
| Q4 | Van×3 | Van=50 |
| Q5 | Van×4 | Van=30 |
| Q6 | Van×3 | Van=36 |
| Q7 | Van×3 | Van=33 |
| Q8 | Van×2 | Van=50 |
| Q9 | Van×4 | Van=20 |
| Q10 | Van×4 | Van=75 |

---

## 🏆 BEST DATASET for Quantum Demo

**`Q1_hexagon_3veh_equal.csv`** with **Van×3, Van_cap=40**

This is the theoretical sweet spot:
- 6 nodes in perfect hexagonal symmetry around depot
- Each pair of adjacent hexagon vertices forms a natural route
- 3 vehicles × 40 cap = 120 total = 6 customers × 20 demand exactly
- Classical NN heuristic has no local preference → gets trapped in suboptimal
- Quantum energy landscape has 3 degenerate global minima → BQPhy finds one reliably

---

## Quick Reference — BQPhy Tier by n_vars (N×K)

| Tier | n_vars | Best dataset | Description |
|------|--------|--------------|-------------|
| Small ≤30 | 6×5=30 | `02_small_6cust_hexagon.csv` (Van×5) | 5 restarts, fast |
| Medium 31–100 | 20×5=100 | `06_medium_20cust_grid.csv` | Auto-scaled |
| Large 101–250 | 50×5=250 | `11_boundary_50cust_nocluster.csv` | Single thorough run |
| XL >250 | 51×6=306 | `12_cluster_51cust.csv` | Clustering activated |
