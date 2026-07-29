from typing import List, Dict, Any, Tuple
from app.models.customer import Customer
from app.models.vehicle import VehicleConfig
import math

class ValidationError(Exception):
    pass

def validate_solution(
    routes: List[List[int]], 
    customers: List[Customer], 
    vehicle_config: VehicleConfig,
    distance_km: float
) -> List[str]:
    errors = []
    
    K = vehicle_config.total_count
    cap_list = vehicle_config.capacities_list
    
    # 1. Fleet Validation
    if len(routes) > K:
        errors.append(f"Fleet exceeded: {len(routes)} routes > {K} vehicles")
        
    # 2. Customer Validation
    customer_assignment = {}
    for route_idx, route in enumerate(routes):
        for node in route[1:-1]:
            if node == 0:
                continue
            if node in customer_assignment:
                errors.append(f"Duplicate assignment: Customer {node} is in route {customer_assignment[node]} and {route_idx}")
            customer_assignment[node] = route_idx
            
    if len(customer_assignment) != len(customers):
        all_ids = set(range(1, len(customers) + 1))
        missing = all_ids - set(customer_assignment.keys())
        if missing:
            errors.append(f"Missing customers: {sorted(missing)}")
            
    # 3. Depot Validation and Route Integrity
    for route_idx, route in enumerate(routes):
        if not route:
            errors.append(f"Route {route_idx} is empty")
            continue
        if route[0] != 0:
            errors.append(f"Route {route_idx} does not start at depot")
        if route[-1] != 0:
            errors.append(f"Route {route_idx} does not end at depot")
        if 0 in route[1:-1]:
            errors.append(f"Route {route_idx} contains depot in the middle")
            
        # Check duplicate customers inside route
        seen = set()
        for node in route[1:-1]:
            if node in seen:
                errors.append(f"Route {route_idx} contains duplicate customer {node}")
            seen.add(node)
            
    # 4. Capacity Validation
    demands = {i+1: c.demand for i, c in enumerate(customers)}
    for route_idx, route in enumerate(routes):
        route_cap = cap_list[route_idx] if route_idx < len(cap_list) else cap_list[-1]
        route_demand = sum(demands.get(node, 0) for node in route if node != 0)
        if route_demand > route_cap + 1e-6:
            errors.append(f"Capacity exceeded in route {route_idx}: {route_demand} > {route_cap}")
            
    # 5. Distance Validation
    if distance_km < 0:
        errors.append(f"Negative distance: {distance_km}")
    if math.isnan(distance_km):
        errors.append("Distance is NaN")
    if math.isinf(distance_km):
        errors.append("Distance is Infinite")
        
    return errors
