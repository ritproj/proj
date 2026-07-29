import json
from fastapi.testclient import TestClient
from app.main import app

def test_full_pipeline_small():
    client = TestClient(app)
    
    # Reset state first
    client.post("/api/reset")

    # Upload configuration with 3 customers (below limit 8)
    csv_data = (
        "Customer_ID,Latitude,Longitude,Demand\n"
        "1,12.9716,77.5946,10.0\n"
        "2,12.9726,77.5956,15.0\n"
        "3,12.9736,77.5966,20.0\n"
    )
    
    fleet = {
        "Van": 2,
        "Truck": 0,
        "Bike": 0,
        "Electric Van": 0
    }
    
    capacities = {
        "Van": 50.0,
        "Truck": 120.0,
        "Bike": 15.0,
        "Electric Van": 60.0
    }

    files = {"file": ("test_small.csv", csv_data, "text/csv")}
    data = {
        "fleet": json.dumps(fleet),
        "capacities": json.dumps(capacities)
    }

    response = client.post("/api/upload", files=files, data=data)
    assert response.status_code == 200
    assert response.json()["customers"] == 3
    assert response.json()["clustering_notice"] is False

    # Run Classical optimization
    response = client.post("/api/classical")
    assert response.status_code == 200
    assert "stats" in response.json()
    assert "routes" in response.json()

    # Run Quantum optimization
    response = client.post("/api/quantum")
    assert response.status_code == 200
    assert "stats" in response.json()
    assert "routes" in response.json()
    # Check that method field is "exhaustive" (N=3, K=2 -> vars = 6 <= 16)
    assert response.json()["method"] == "exhaustive"
    assert response.json()["fallback_used"] is False

    # Get Benchmark
    response = client.get("/api/benchmark")
    assert response.status_code == 200
    assert response.json()["winner"] in ["classical", "quantum", "tie"]
    assert response.json()["quantum"]["method"] == "exhaustive"

    # Reset
    response = client.post("/api/reset")
    assert response.status_code == 200

def test_full_pipeline_clustered():
    client = TestClient(app)
    client.post("/api/reset")

    # Upload configuration with 10 customers (above limit 8)
    csv_data = "Customer_ID,Latitude,Longitude,Demand\n"
    for i in range(1, 11):
        csv_data += f"{i},12.9716,77.5946,10.0\n"

    fleet = {
        "Van": 3,
        "Truck": 0,
        "Bike": 0,
        "Electric Van": 0
    }
    
    capacities = {
        "Van": 50.0,
        "Truck": 120.0,
        "Bike": 15.0,
        "Electric Van": 60.0
    }

    files = {"file": ("test_large.csv", csv_data, "text/csv")}
    data = {
        "fleet": json.dumps(fleet),
        "capacities": json.dumps(capacities)
    }

    response = client.post("/api/upload", files=files, data=data)
    assert response.status_code == 200
    assert response.json()["customers"] == 10
    assert response.json()["clustering_notice"] is True

    # Run Quantum optimization (should cluster into groups of <=8)
    response = client.post("/api/quantum")
    assert response.status_code == 200
    # Because it is clustered, it will solve each cluster (which has size <= 8 customers)
    # The variables count of each cluster will determine the solver method for the cluster.
    # Total customers per cluster <= 8. Let's make sure it returned valid routes.
    assert len(response.json()["routes"]) > 0
    assert "stats" in response.json()
    assert "method" in response.json()
    # It must not crash, and should return a valid solver method name.
    assert response.json()["method"] in ["exhaustive", "simulated_annealing", "nn_fallback"]
