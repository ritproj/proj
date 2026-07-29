import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from app.models.vehicle import VehicleConfig
from app.services.qaoa_solver import solve_quantum
from tests.framework.generators import generate_customers, generate_depot

depot = generate_depot("center")
customers = generate_customers(10, "random", "random", 25.0)
demands = [20, 20, 20, 30, 20, 25, 25, 30, 20, 17]
for c, d in zip(customers, demands):
    c.demand = d
fleet = VehicleConfig(fleet={"Van": 2, "Truck": 1}, capacities={"Van": 70.0, "Truck": 120.0})

res = solve_quantum(depot, customers, fleet, bypass_clustering=False)
print("Feasible:", res.feasible)
if not res.feasible:
    print("Infeasible Reason:", getattr(res, 'infeasible_reason', None))

for i, r in enumerate(res.routes):
    cap = fleet.capacities_list[i]
    vtype = fleet.vehicle_types_list[i]
    load = sum(c.demand for c in customers if c.customer_id in r)
    print(f"Route {i} - {vtype} ({cap}kg) - Load: {load}kg - Route: {r}")
