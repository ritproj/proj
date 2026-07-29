import random
import math
from typing import List, Dict, Tuple
from app.models.customer import Customer
from app.models.depot import Depot
from app.models.vehicle import VehicleConfig

def generate_depot(location_type="center") -> Depot:
    if location_type == "center":
        return Depot(latitude=0.0, longitude=0.0)
    elif location_type == "edge":
        return Depot(latitude=90.0, longitude=180.0)
    elif location_type == "outside":
        return Depot(latitude=150.0, longitude=200.0) # Invalid in strict geographic bounds, but good for stress test
    return Depot(latitude=0.0, longitude=0.0)


def generate_customers(size: int, layout: str, demand_profile: str, capacity: float) -> List[Customer]:
    customers = []
    
    for i in range(size):
        # Coordinates
        lat, lon = 0.0, 0.0
        if layout == "random":
            lat = random.uniform(-90, 90)
            lon = random.uniform(-180, 180)
        elif layout == "dense_cluster":
            lat = random.uniform(-1, 1)
            lon = random.uniform(-1, 1)
        elif layout == "grid":
            lat = float(i % int(math.sqrt(size) + 1)) * 5.0
            lon = float(i // int(math.sqrt(size) + 1)) * 5.0
        elif layout == "spiral":
            radius = i * 0.5
            angle = i * 0.5
            lat = radius * math.cos(angle)
            lon = radius * math.sin(angle)
        elif layout == "star":
            angle = (i * 2 * math.pi) / max(1, size)
            lat = 10 * math.cos(angle)
            lon = 10 * math.sin(angle)
        elif layout == "straight_line":
            lat = float(i)
            lon = float(i)
        elif layout == "identical":
            lat, lon = 10.0, 10.0
        else: # default random
            lat = random.uniform(-50, 50)
            lon = random.uniform(-50, 50)
            
        # Demand
        demand = 10.0
        if demand_profile == "equal":
            demand = min(10.0, capacity - 1) if capacity > 0 else 10.0
        elif demand_profile == "random":
            demand = random.uniform(1, capacity if capacity > 0 else 100)
        elif demand_profile == "high":
            demand = capacity * 0.9 if capacity > 0 else 100.0
        elif demand_profile == "low":
            demand = capacity * 0.1 if capacity > 0 else 1.0
        elif demand_profile == "equal_capacity":
            demand = capacity
        elif demand_profile == "exceed_capacity":
            demand = capacity + 50.0
        
        customers.append(Customer(customer_id=i+1, latitude=lat, longitude=lon, demand=demand))
        
    return customers


def generate_fleet(fleet_type: str) -> VehicleConfig:
    fleet_dict = {}
    capacities_dict = {}
    
    if fleet_type == "single":
        fleet_dict = {"Van": 1}
        capacities_dict = {"Van": 70.0}
    elif fleet_type == "two":
        fleet_dict = {"Van": 2}
        capacities_dict = {"Van": 70.0}
    elif fleet_type == "three":
        fleet_dict = {"Van": 3}
        capacities_dict = {"Van": 70.0}
    elif fleet_type == "mixed":
        fleet_dict = {"Van": 2, "Truck": 1}
        capacities_dict = {"Van": 70.0, "Truck": 120.0}
    elif fleet_type == "large":
        fleet_dict = {"Van": 5, "Truck": 5}
        capacities_dict = {"Van": 70.0, "Truck": 120.0}
    elif fleet_type == "random":
        v = random.randint(1, 5)
        t = random.randint(0, 5)
        if v == 0 and t == 0:
            v = 1
        if v > 0:
            fleet_dict["Van"] = v
            capacities_dict["Van"] = random.uniform(50.0, 100.0)
        if t > 0:
            fleet_dict["Truck"] = t
            capacities_dict["Truck"] = random.uniform(100.0, 200.0)
    elif fleet_type == "huge_capacity":
        fleet_dict = {"Van": 1}
        capacities_dict = {"Van": 999999.0}
    elif fleet_type == "tiny_capacity":
        fleet_dict = {"Truck": 2}
        capacities_dict = {"Truck": 1.0}
    else:
        fleet_dict = {"Van": 3}
        capacities_dict = {"Van": 70.0}
        
    return VehicleConfig(fleet=fleet_dict, capacities=capacities_dict)
