import numpy as np
from app.models.customer import Customer
from app.services.qubo import build_qubo, variable_count

def test_variable_count():
    assert variable_count(5, 3) == 15
    assert variable_count(8, 2) == 16

def test_build_qubo_shape():
    # Setup simple dataset: depot and 2 customers, 2 vehicles
    # Distances: depot is at 0. Customers at 1, 2.
    dist_matrix = np.array([
        [0.0, 1.0, 2.0],
        [1.0, 0.0, 1.5],
        [2.0, 1.5, 0.0]
    ])
    customers = [
        Customer(customer_id=1, latitude=0.1, longitude=0.1, demand=10.0),
        Customer(customer_id=2, latitude=0.2, longitude=0.2, demand=20.0),
    ]
    capacities = [50.0, 50.0]
    n_vehicles = 2

    Q, n_vars, penalty = build_qubo(dist_matrix, customers, n_vehicles, capacities)

    # 2 customers * 2 vehicles = 4 variables
    assert n_vars == 4
    assert penalty > 0
    # Q should contain keys as pairs of variables
    assert len(Q) > 0
    # Variables should be within 0..n_vars-1
    for (a, b), val in Q.items():
        assert 0 <= a < n_vars
        assert 0 <= b < n_vars
        assert a <= b
