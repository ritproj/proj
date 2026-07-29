import sys
import os
import numpy as np
from typing import List, Optional, Dict
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from app.models.customer import Customer
from app.models.depot import Depot
from app.models.vehicle import VehicleConfig
import app.services.qaoa_solver as qaoa_solver
from app.services.qaoa_solver import solve_quantum, QuantumResult
from tests.framework.generators import generate_customers, generate_depot

def _solve_clustered_quantum_proof(depot: Depot, customers: List[Customer], vehicle_config: VehicleConfig) -> QuantumResult:
    # EXACT COPY but with print statements
    dist_matrix = qaoa_solver.build_distance_matrix(depot, customers)
    K = vehicle_config.total_count
    cap_list = vehicle_config.capacities_list  # [70, 70, 120]

    print("1. Original Fleet (Global Vehicle List):")
    for i, (cap, vtype) in enumerate(zip(cap_list, vehicle_config.vehicle_types_list)):
        print(f"Global Vehicle {i} -> {vtype} ({cap} kg)")
    print("\n")

    n_clusters = (len(customers) + qaoa_solver.QAOA_CUSTOMER_LIMIT - 1) // qaoa_solver.QAOA_CUSTOMER_LIMIT
    n_clusters = max(1, min(n_clusters, K))
    from app.services.dataset import cluster_customers
    geo_clusters = cluster_customers(customers, n_clusters)
    n_clusters = len(geo_clusters)

    # Phase A & B
    vehicles = []
    for i, (cap, vtype) in enumerate(zip(cap_list, vehicle_config.vehicle_types_list)):
        vehicles.append({"capacity": cap, "type": vtype, "global_idx": i})
    
    vehicles = sorted(vehicles, key=lambda v: v["capacity"], reverse=True)
    
    cluster_demands = [sum(c.demand for c in cl) for cl in geo_clusters]
    demand_order = list(np.argsort(cluster_demands)[::-1])
    
    allocations: List[List[dict]] = [[] for _ in range(n_clusters)]
    pool = list(vehicles)
    
    for idx in demand_order:
        if pool:
            allocations[idx].append(pool.pop(0))
            
    while pool:
        veh = pool.pop(0)
        unsatisfied = [cluster_demands[i] - sum(v["capacity"] for v in allocations[i]) for i in range(n_clusters)]
        allocations[int(np.argmax(unsatisfied))].append(veh)

    print("2. During Clustering:")
    cluster_configs: List[VehicleConfig] = []
    for idx, alloc in enumerate(allocations):
        print(f"Cluster {idx}:")
        print(f"- Customers: {[c.customer_id for c in geo_clusters[idx]]}")
        print(f"- Demand: {cluster_demands[idx]} kg")
        fleet_dict:  Dict[str, int]   = {}
        caps_dict:   Dict[str, float] = {}
        for veh in alloc:
            vt = veh["type"]
            fleet_dict[vt] = fleet_dict.get(vt, 0) + 1
            caps_dict[vt]  = veh["capacity"]
            print(f"- Vehicle assigned: {veh['type']} ({veh['capacity']} kg) -> Original Global Vehicle {veh['global_idx']}")
        cluster_configs.append(VehicleConfig(fleet=fleet_dict, capacities=caps_dict))
    print("\n")

    print("3. Before combining routes (Mapping):")
    vehicle_routes: List[Optional[List[int]]] = [None] * K
    vehicle_cursor = 0
    
    for cl_idx, (cl, cl_cfg) in enumerate(zip(geo_clusters, cluster_configs)):
        ki  = cl_cfg.total_count
        res = solve_quantum(depot, cl, cl_cfg, bypass_clustering=True)
        
        mapped: List[List[int]] = []
        for r in res.routes:
            m: List[int] = []
            for node in r:
                if node == 0:
                    m.append(0)
                else:
                    orig_idx = customers.index(cl[node - 1]) + 1
                    m.append(orig_idx)
            if len(m) > 2:
                mapped.append(m)
                
        for i, route in enumerate(mapped):
            slot = vehicle_cursor + i
            if slot < K:
                vehicle_routes[slot] = route
            print(f"Cluster {cl_idx} Route {i} placed at slot {slot}")
        vehicle_cursor += ki
    print("\n")

    print("4. After combining routes:")
    combined_routes = [r for r in vehicle_routes if r is not None]
    for r_idx, route in enumerate(combined_routes):
        print(f"Returned Route {r_idx}")
        mapped_cap = cap_list[r_idx]
        mapped_type = vehicle_config.vehicle_types_list[r_idx]
        load = sum(c.demand for c in customers if c.customer_id in route)
        print(f"Mapped Vehicle: {mapped_type}")
        print(f"Vehicle Capacity: {mapped_cap} kg")
        print(f"Route Load: {load} kg")
        status = 'PASS' if load <= mapped_cap else 'FAIL'
        print(f"Status: {status}")
        print("-")
    print("\n")
    
    print("5. Verification against Original Global Vehicle:")
    # We need to map returned routes back to their true original vehicles
    true_mapping = []
    for alloc in allocations:
        for veh in alloc:
            true_mapping.append(veh)
            
    for r_idx, route in enumerate(combined_routes):
        load = sum(c.demand for c in customers if c.customer_id in route)
        mapped_cap = cap_list[r_idx]
        mapped_type = vehicle_config.vehicle_types_list[r_idx]
        original_veh = true_mapping[r_idx]
        
        print(f"Route {r_idx} (Load = {load} kg)")
        print(f"Assigned to {mapped_type} ({mapped_cap} kg) {'PASS' if load <= mapped_cap else 'FAIL'}")
        print(f"Original Vehicle was {original_veh['type']} ({original_veh['capacity']} kg) {'PASS' if load <= original_veh['capacity'] else 'FAIL'}")
        print("-")
        
    return res

# Patch it
qaoa_solver._solve_clustered_quantum = _solve_clustered_quantum_proof

depot = generate_depot("center")
customers = generate_customers(10, "random", "random", 25.0)
demands = [20, 20, 20, 30, 20, 25, 25, 30, 20, 17]
for c, d in zip(customers, demands):
    c.demand = d
fleet = VehicleConfig(fleet={"Van": 2, "Truck": 1}, capacities={"Van": 70.0, "Truck": 120.0})

solve_quantum(depot, customers, fleet, bypass_clustering=False)
