import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from app.models.vehicle import VehicleConfig
from app.services.qaoa_solver import solve_quantum
from app.utils.helpers import routes_to_frontend
from tests.framework.generators import generate_customers, generate_depot

depot = generate_depot("center")
customers = generate_customers(10, "random", "random", 25.0)
demands = [20, 20, 20, 30, 20, 25, 25, 30, 20, 17]
for c, d in zip(customers, demands):
    c.demand = d

vehicle_config = VehicleConfig(fleet={"Van": 2, "Truck": 1}, capacities={"Van": 70.0, "Truck": 120.0})

print("1. Internal vehicle list before solving (from VehicleConfig):")
for i, (vt, cap) in enumerate(zip(vehicle_config.vehicle_types_list, vehicle_config.capacities_list)):
    print(f"   Global Vehicle {i} -> Type: {vt}, Capacity: {cap}")
print("\n")

print("2-4. (Covered implicitly by QAOA backend logs)\n")

result = solve_quantum(depot, customers, vehicle_config, bypass_clustering=False)

print("5. QuantumResult before returning (from qaoa_solver.py):")
print(f"   Number of active routes returned: {len(result.routes)}")
for i, r in enumerate(result.routes):
    print(f"   Result Route {i}: {r}")
print("\n")

print("6. API Layer (app/routes/quantum.py):")
vtypes = vehicle_config.vehicle_types_list[:len(result.routes)]
vcaps = vehicle_config.capacities_list[:len(result.routes)]
print(f"   Slices vehicle_types_list[:{len(result.routes)}] -> {vtypes}")
print(f"   Slices capacities_list[:{len(result.routes)}] -> {vcaps}")

map_data = routes_to_frontend(
    result.routes,
    depot,
    customers,
    vehicle_types=vtypes,
    vehicle_caps=vcaps,
    dist_matrix=result.distance_matrix,
)

print("\n7. Frontend Route Parsing Simulation (from map_data):")
for i, route_meta in enumerate(map_data["route_meta"]):
    print(f"   Parsed Route {i}:")
    print(f"      Global vehicle index (assumed): {i}")
    print(f"      Vehicle type assigned by API: {route_meta['type']}")
    print(f"      Capacity assigned by API: {route_meta['capacity_kg']}")
    print(f"      Calculated Load: {route_meta['load_kg']}")
print("\n")

print("8. Route Breakdown Component Render (Frontend):")
for i, route_meta in enumerate(map_data["route_meta"]):
    load = route_meta['load_kg']
    cap = route_meta['capacity_kg']
    vt = route_meta['type']
    status = "FAIL" if load > cap else "PASS"
    print(f"   Vehicle {i+1} ({vt}): {load} kg / {cap} kg  -> {status}")
print("\n")

print("--- ROOT CAUSE VERIFICATION ---")
print("The backend returned Feasible = ", result.feasible)
if not result.feasible:
    print("Violations:", getattr(result, 'infeasible_reason', 'Unknown'))
if result.feasible:
    print("Backend solver successfully routed everything within absolute global capacities.")
    print("But the frontend renders an overloaded vehicle. The mismatch happens at Step 6 (API Layer).")
    print("The API strips 'None' routes from `result.routes`, then blindly zips the remaining active routes")
    print("against the first N capacities of `VehicleConfig`, breaking the global index mapping.")
