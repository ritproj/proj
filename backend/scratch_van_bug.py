import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from app.models.customer import Customer
from app.models.depot import Depot
from app.models.vehicle import VehicleConfig
from app.services.qaoa_solver import solve_quantum
from tests.framework.generators import generate_customers, generate_depot

depot = generate_depot("center")
customers = generate_customers(10, "random", "random", 25.0)

demands = [20, 20, 20, 30, 20, 25, 25, 30, 20, 17]
for c, d in zip(customers, demands):
    c.demand = d

fleet = VehicleConfig(fleet={"Van": 2, "Truck": 1}, capacities={"Van": 70.0, "Truck": 120.0})

from app.services.repair import validate_routes
res = solve_quantum(depot, customers, fleet, bypass_clustering=False)
print(f"Feasible: {res.feasible}")
print(f"Infeasible Reason: {getattr(res, 'infeasible_reason', None)}")

if not res.feasible:
    print(f"Wait, validate_routes check:")
    valid, violations = validate_routes(res.routes, customers, fleet.capacities_list)
    print(violations)

for idx, r in enumerate(res.routes):
    cap = fleet.capacities_list[idx] if idx < len(fleet.capacities_list) else fleet.capacities_list[-1]
    load = sum(c.demand for c in customers if c.customer_id in r)
    print(f"Vehicle {idx+1}: {load} kg (Capacity: {cap} kg) - Route: {r}")
