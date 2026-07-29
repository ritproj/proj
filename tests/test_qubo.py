# tests/test_qubo.py

import numpy as np
from app.services.qubo import build_qubo, variable_count
from app.models.customer import Customer
from app.models.depot import Depot
from app.models.vehicle import VehicleConfig

def test_variable_count_simple():
    # Simple distance matrix for 2 customers
    dist = np.array([[0, 10], [10, 0]])
    n = dist.shape[0]
    n_vars = variable_count(n, 2)
    assert n_vars == n * 2  # N*K

def test_build_qubo_structure():
    # Minimal mock objects
    depot = Depot(id=0, lat=0.0, lon=0.0)
    customers = [Customer(id=1, lat=0.1, lon=0.1, demand=1.0),
                 Customer(id=2, lat=0.2, lon=0.2, demand=1.0)]
    vehicle_config = VehicleConfig(total_count=2, capacities_list=[10.0, 10.0], fleet={}, vehicle_types_list=[])
    dist_matrix = np.array([[0, 10, 15], [10, 0, 5], [15, 5, 0]])
    qubo, n_vars, _ = build_qubo(dist_matrix, customers, n_vehicles=2, capacities=vehicle_config.capacities_list)
    assert isinstance(qubo, dict)
    assert n_vars == variable_count(len(customers), 2)
