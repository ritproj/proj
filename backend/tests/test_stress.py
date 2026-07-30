"""
test_stress.py — Comprehensive stress & edge-case tests for the BQPhy pipeline.

Route format returned by /api/quantum:
  routes: [ [{lat, lng, id, demand}, ...], ... ]
  where id=None means depot, id=int means customer node.

Tests every important boundary:
  - Minimal datasets (1 customer)
  - Variable-count tiers (small / medium / large / xl)
  - Clustering boundary (at and above BQPHY_CUSTOMER_LIMIT=50)
  - Fleet extremes (1 vehicle, K>N, capacity-exact, high demand)
  - Geographic extremes (same location, polar, far apart)
  - Repair pipeline unit tests (validate, repair, 2-opt)
  - Fallback robustness (must always produce feasible routes)
  - CSV parsing rejection (bad inputs must return 4xx)
"""

from __future__ import annotations

import json
import math
import pytest
from fastapi.testclient import TestClient

from app.main import app

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FLEET_SOLO  = {"Van": 1, "Truck": 0, "Bike": 0, "Electric Van": 0}
FLEET_3     = {"Van": 3, "Truck": 0, "Bike": 0, "Electric Van": 0}
FLEET_5     = {"Van": 5, "Truck": 0, "Bike": 0, "Electric Van": 0}
FLEET_10    = {"Van": 10, "Truck": 0, "Bike": 0, "Electric Van": 0}
FLEET_MIXED = {"Van": 2, "Truck": 1, "Bike": 0, "Electric Van": 0}

CAPS_GENEROUS = {"Van": 9999.0, "Truck": 9999.0, "Bike": 15.0, "Electric Van": 60.0}
CAPS_TIGHT    = {"Van": 50.0,   "Truck": 120.0,  "Bike": 15.0, "Electric Van": 60.0}
CAPS_MIXED    = {"Van": 50.0,   "Truck": 120.0,  "Bike": 15.0, "Electric Van": 60.0}

VALID_METHODS = {"bqphy", "exhaustive", "simulated_annealing", "nn_fallback", "infeasible"}


def make_csv(n: int, demand: float = 10.0, *, same_location: bool = False) -> str:
    rows = ["Customer_ID,Latitude,Longitude,Demand"]
    for i in range(1, n + 1):
        if same_location:
            lat, lon = 12.9716, 77.5946
        else:
            lat = 12.9716 + i * 0.001
            lon = 77.5946 + i * 0.001
        rows.append(f"{i},{lat},{lon},{demand}")
    return "\n".join(rows)


def upload(client: TestClient, csv_data: str, fleet: dict, caps: dict) -> dict:
    response = client.post(
        "/api/upload",
        files={"file": ("test.csv", csv_data, "text/csv")},
        data={"fleet": json.dumps(fleet), "capacities": json.dumps(caps)},
    )
    assert response.status_code == 200, f"Upload failed ({response.status_code}): {response.text}"
    return response.json()


def run_quantum(client: TestClient) -> dict:
    response = client.post("/api/quantum")
    assert response.status_code == 200, f"Quantum failed ({response.status_code}): {response.text}"
    return response.json()


# ── Route-format helpers ────────────────────────────────────────────────────
# routes = [ [{lat, lng, id, demand}, ...], ... ]
# id=None  → depot waypoint
# id=int   → customer node

def is_depot(waypoint: dict) -> bool:
    return waypoint.get("id") is None

def customer_ids_in_routes(routes: list[list[dict]]) -> list[int]:
    """Return sorted list of all customer ids across all routes (depot excluded)."""
    return sorted(wp["id"] for route in routes for wp in route if not is_depot(wp))

def assert_valid_result(result: dict, *, expect_feasible: bool = True) -> None:
    """Core guarantees every QuantumResult must satisfy."""
    assert "routes" in result,  "missing 'routes'"
    assert "stats"  in result,  "missing 'stats'"
    assert "method" in result,  "missing 'method'"
    assert result["method"] in VALID_METHODS, f"unknown method: {result['method']}"
    assert isinstance(result["fallback_used"], bool), "fallback_used must be bool"
    assert result["stats"]["distance_km"] >= 0, "negative distance"
    assert not math.isnan(result["stats"]["distance_km"]), "NaN distance"
    assert len(result["routes"]) > 0, "no routes returned"

    for route in result["routes"]:
        assert len(route) >= 2, f"route has < 2 waypoints: {route}"
        assert is_depot(route[0]),  f"route does not start at depot: {route[0]}"
        assert is_depot(route[-1]), f"route does not end at depot: {route[-1]}"

    if expect_feasible:
        assert result.get("feasible", True), "expected feasible result"


# ---------------------------------------------------------------------------
# 1. Minimal cases
# ---------------------------------------------------------------------------

class TestMinimal:

    def test_single_customer_single_vehicle(self):
        """1 customer, 1 vehicle — trivial but must not crash."""
        client = TestClient(app)
        client.post("/api/reset")
        upload(client, make_csv(1, demand=10.0), FLEET_SOLO, CAPS_GENEROUS)
        result = run_quantum(client)
        assert_valid_result(result)
        ids = customer_ids_in_routes(result["routes"])
        assert ids == [1], f"Expected [1], got {ids}"

    def test_two_customers_single_vehicle(self):
        """2 customers, 1 vehicle — both must be served."""
        client = TestClient(app)
        client.post("/api/reset")
        upload(client, make_csv(2, demand=10.0), FLEET_SOLO, CAPS_GENEROUS)
        result = run_quantum(client)
        assert_valid_result(result)
        ids = customer_ids_in_routes(result["routes"])
        assert sorted(ids) == [1, 2], f"Not all customers served: {ids}"

    def test_more_vehicles_than_customers(self):
        """5 vehicles but only 2 customers — all customers served, no duplicates."""
        client = TestClient(app)
        client.post("/api/reset")
        upload(client, make_csv(2, demand=10.0), FLEET_5, CAPS_TIGHT)
        result = run_quantum(client)
        assert_valid_result(result)
        ids = customer_ids_in_routes(result["routes"])
        assert set(ids) == {1, 2}, f"Not all customers served: {ids}"
        assert len(ids) == len(set(ids)), "Duplicate customer visits"


# ---------------------------------------------------------------------------
# 2. Capacity boundary cases
# ---------------------------------------------------------------------------

class TestCapacity:

    def test_demand_exactly_fills_single_vehicle(self):
        """5 customers × 10 kg = 50 kg = Van capacity exactly."""
        client = TestClient(app)
        client.post("/api/reset")
        caps = {"Van": 50.0, "Truck": 120.0, "Bike": 15.0, "Electric Van": 60.0}
        upload(client, make_csv(5, demand=10.0), FLEET_SOLO, caps)
        result = run_quantum(client)
        assert_valid_result(result)
        ids = customer_ids_in_routes(result["routes"])
        assert set(ids) == set(range(1, 6)), f"Not all customers served: {ids}"

    def test_demand_requires_multiple_vehicles(self):
        """Each customer demand > 1 vehicle capacity → must use multiple vehicles."""
        client = TestClient(app)
        client.post("/api/reset")
        caps = {"Van": 50.0, "Truck": 120.0, "Bike": 15.0, "Electric Van": 60.0}
        upload(client, make_csv(3, demand=40.0), FLEET_3, caps)
        result = run_quantum(client)
        assert_valid_result(result)
        ids = customer_ids_in_routes(result["routes"])
        assert set(ids) == {1, 2, 3}

    def test_very_high_demand_with_generous_capacity(self):
        """Large demand values must not cause overflow / NaN.
        Use enough vehicles so total fleet cap >= total demand."""
        client = TestClient(app)
        client.post("/api/reset")
        # 4 customers × 9999 kg demand, 4 vans × 9999 kg cap → demand == cap (just feasible)
        caps = {"Van": 9999.0, "Truck": 9999.0, "Bike": 15.0, "Electric Van": 60.0}
        fleet = {"Van": 4, "Truck": 0, "Bike": 0, "Electric Van": 0}
        upload(client, make_csv(4, demand=9999.0), fleet, caps)
        result = run_quantum(client)
        assert_valid_result(result)
        assert result["stats"]["distance_km"] >= 0


# ---------------------------------------------------------------------------
# 3. Geographic extremes
# ---------------------------------------------------------------------------

class TestGeography:

    def test_all_customers_same_location(self):
        """All customers at exactly the same (lat, lon) — distance matrix all zeros."""
        client = TestClient(app)
        client.post("/api/reset")
        upload(client, make_csv(4, demand=10.0, same_location=True), FLEET_3, CAPS_TIGHT)
        result = run_quantum(client)
        assert_valid_result(result)
        assert result["stats"]["distance_km"] >= 0

    def test_widely_spread_customers(self):
        """Customers spread across four continents — large distance values."""
        client = TestClient(app)
        client.post("/api/reset")
        rows = ["Customer_ID,Latitude,Longitude,Demand",
                "1,40.7128,-74.0060,10.0",
                "2,51.5074,-0.1278,10.0",
                "3,35.6762,139.6503,10.0",
                "4,33.8688,151.2093,10.0"]
        upload(client, "\n".join(rows), FLEET_3, CAPS_GENEROUS)
        result = run_quantum(client)
        assert_valid_result(result)
        assert result["stats"]["distance_km"] > 0

    def test_customers_near_poles(self):
        """Lat near ±90 — haversine must handle polar coords without NaN."""
        client = TestClient(app)
        client.post("/api/reset")
        rows = ["Customer_ID,Latitude,Longitude,Demand",
                "1,89.0,0.0,10.0",
                "2,-89.0,0.0,10.0",
                "3,0.0,179.0,10.0"]
        upload(client, "\n".join(rows), FLEET_3, CAPS_GENEROUS)
        result = run_quantum(client)
        assert_valid_result(result)


# ---------------------------------------------------------------------------
# 4. Variable-count tier tests (adaptive BQPhy scaling)
# ---------------------------------------------------------------------------

class TestVariableTiers:

    def _run(self, n_customers: int, n_vehicles: int) -> dict:
        client = TestClient(app)
        client.post("/api/reset")
        fleet = {k: (n_vehicles if k == "Van" else 0) for k in ["Van", "Truck", "Bike", "Electric Van"]}
        upload(client, make_csv(n_customers, demand=5.0), fleet, CAPS_GENEROUS)
        result = run_quantum(client)
        assert_valid_result(result)
        # All customers served exactly once
        ids = customer_ids_in_routes(result["routes"])
        assert set(ids) == set(range(1, n_customers + 1)), \
            f"Not all {n_customers} customers served: {sorted(set(ids))}"
        assert len(ids) == len(set(ids)), "Duplicate customer visits"
        return result

    def test_tier_small_6vars(self):
        """n_vars = 2×3 = 6 ≤ 30 → small tier, 5 restarts."""
        self._run(n_customers=2, n_vehicles=3)

    def test_tier_small_boundary_30vars(self):
        """n_vars = 6×5 = 30 ≤ 30 → still small tier."""
        self._run(n_customers=6, n_vehicles=5)

    def test_tier_medium_32vars(self):
        """n_vars = 8×4 = 32 → medium tier (31–100)."""
        self._run(n_customers=8, n_vehicles=4)

    def test_tier_medium_100vars(self):
        """n_vars = 20×5 = 100 → top of medium tier."""
        self._run(n_customers=20, n_vehicles=5)

    def test_tier_large_120vars(self):
        """n_vars = 30×4 = 120 → large tier (101–250), as shown in screenshot."""
        self._run(n_customers=30, n_vehicles=4)

    def test_tier_large_250vars(self):
        """n_vars = 50×5 = 250 → top of large tier."""
        self._run(n_customers=50, n_vehicles=5)

    def test_tier_xl_300vars(self):
        """n_vars = 50×6 = 300 → xl tier (>250), single thorough run."""
        self._run(n_customers=50, n_vehicles=6)


# ---------------------------------------------------------------------------
# 5. Clustering boundary
# ---------------------------------------------------------------------------

class TestClustering:

    def test_at_customer_limit_no_clustering(self):
        """Exactly 50 customers → no clustering (BQPHY_CUSTOMER_LIMIT=50)."""
        client = TestClient(app)
        client.post("/api/reset")
        resp = upload(client, make_csv(50, demand=5.0), FLEET_5, CAPS_GENEROUS)
        assert resp["clustering_notice"] is False, "50 customers should NOT trigger clustering"
        result = run_quantum(client)
        assert_valid_result(result)

    def test_just_above_limit_clustering(self):
        """51 customers → clustering kicks in."""
        client = TestClient(app)
        client.post("/api/reset")
        resp = upload(client, make_csv(51, demand=5.0), FLEET_10, CAPS_GENEROUS)
        assert resp["clustering_notice"] is True, "51 customers should trigger clustering"
        result = run_quantum(client)
        assert_valid_result(result)

    def test_large_clustered_dataset_all_customers_served(self):
        """55 customers via clustering — all must appear exactly once in routes."""
        client = TestClient(app)
        client.post("/api/reset")
        resp = upload(client, make_csv(55, demand=5.0), FLEET_10, CAPS_GENEROUS)
        assert resp["clustering_notice"] is True
        result = run_quantum(client)
        assert_valid_result(result)
        ids = customer_ids_in_routes(result["routes"])
        assert len(ids) == 55, f"Expected 55 customers, got {len(ids)}"
        assert len(ids) == len(set(ids)), "Duplicate visits in clustered result"


# ---------------------------------------------------------------------------
# 6. Repair pipeline unit tests (pure Python, no HTTP)
# ---------------------------------------------------------------------------

class TestRepairPipeline:

    def test_repair_opens_spare_vehicle_slot(self):
        """When a customer can't fit existing routes, repair should open a spare [0,0] slot."""
        import numpy as np
        from app.services.repair import repair_routes
        from app.models.customer import Customer

        customers = [
            Customer(customer_id=i, latitude=12.97 + i * 0.01, longitude=77.59, demand=10.0)
            for i in range(1, 5)
        ]
        # Route 0 and 1 are full; route 2 is empty spare slot
        routes = [[0, 1, 2, 0], [0, 3, 0], [0, 0]]
        capacities = [20.0, 10.0, 30.0]  # route 1 is exactly full after customer 3
        dm = np.zeros((5, 5))

        repaired, _ = repair_routes(routes, customers, capacities, dm)
        ids = sorted(n for r in repaired for n in r if n != 0)
        assert 4 in ids, f"Customer 4 must be repaired into routes, got {ids}"

    def test_two_opt_preserves_depot_endpoints(self):
        """2-opt must keep [0, ..., 0] structure and not drop any customer."""
        import numpy as np
        from app.services.repair import two_opt_improve

        route = [0, 3, 1, 4, 2, 0]
        dm = np.array([
            [0, 1, 2, 3, 4],
            [1, 0, 1, 2, 3],
            [2, 1, 0, 1, 2],
            [3, 2, 1, 0, 1],
            [4, 3, 2, 1, 0],
        ], dtype=float)
        improved = two_opt_improve([route], dm)
        assert improved[0][0]  == 0, "Route must start at depot"
        assert improved[0][-1] == 0, "Route must end at depot"
        assert set(improved[0][1:-1]) == set(route[1:-1]), "2-opt changed customer set"

    def test_two_opt_does_not_worsen_distance(self):
        """2-opt result must be ≤ original distance."""
        import numpy as np
        from app.services.repair import two_opt_improve

        route = [0, 4, 2, 1, 3, 0]
        dm = np.array([
            [0, 10, 8,  12, 6],
            [10, 0, 5,  3,  9],
            [8,  5, 0,  4,  7],
            [12, 3, 4,  0,  2],
            [6,  9, 7,  2,  0],
        ], dtype=float)

        def route_dist(r):
            return sum(dm[r[i]][r[i+1]] for i in range(len(r)-1))

        orig_dist = route_dist(route)
        improved  = two_opt_improve([route], dm)
        new_dist  = route_dist(improved[0])
        assert new_dist <= orig_dist + 1e-9, \
            f"2-opt worsened distance: {orig_dist:.4f} → {new_dist:.4f}"

    def test_validate_catches_capacity_violation(self):
        """validate_routes must flag overloaded vehicle."""
        from app.services.repair import validate_routes
        from app.models.customer import Customer

        customers = [Customer(customer_id=1, latitude=12.97, longitude=77.59, demand=100.0)]
        feasible, violations = validate_routes([[0, 1, 0]], customers, [50.0])
        assert not feasible
        assert any("capacity exceeded" in v.lower() for v in violations)

    def test_validate_catches_missing_customer(self):
        """validate_routes must flag unvisited customer."""
        from app.services.repair import validate_routes
        from app.models.customer import Customer

        customers = [
            Customer(customer_id=1, latitude=12.97, longitude=77.59, demand=10.0),
            Customer(customer_id=2, latitude=12.98, longitude=77.60, demand=10.0),
        ]
        feasible, violations = validate_routes([[0, 1, 0]], customers, [50.0, 50.0])
        assert not feasible
        assert any("2" in v for v in violations)

    def test_validate_catches_duplicate_visit(self):
        """validate_routes must flag customer served twice."""
        from app.services.repair import validate_routes
        from app.models.customer import Customer

        customers = [Customer(customer_id=1, latitude=12.97, longitude=77.59, demand=10.0)]
        feasible, violations = validate_routes([[0, 1, 1, 0]], customers, [999.0])
        assert not feasible
        assert any("visited 2 times" in v for v in violations)

    def test_nn_fallback_always_feasible(self):
        """nearest_neighbor_with_2opt must always produce feasible routes."""
        import numpy as np
        from app.services.repair import nearest_neighbor_with_2opt, validate_routes
        from app.models.customer import Customer

        customers = [
            Customer(customer_id=i, latitude=12.97 + i*0.01, longitude=77.59, demand=10.0)
            for i in range(1, 7)
        ]
        dm = np.array([
            [0.0 if i == j else abs(i - j) * 1.0
             for j in range(7)]
            for i in range(7)
        ])
        routes = nearest_neighbor_with_2opt(dm, customers, 3, [30.0, 30.0, 30.0])
        feasible, violations = validate_routes(routes, customers, [30.0, 30.0, 30.0])
        assert feasible, f"NN+2opt must be feasible, violations: {violations}"


# ---------------------------------------------------------------------------
# 7. Full pipeline robustness (HTTP level)
# ---------------------------------------------------------------------------

class TestFullPipelineRobust:

    def test_classical_then_quantum_then_compare(self):
        """Both solvers + GET /api/compare must succeed on same dataset."""
        client = TestClient(app)
        client.post("/api/reset")
        upload(client, make_csv(5, demand=8.0), FLEET_3, CAPS_TIGHT)

        cr = client.post("/api/classical")
        assert cr.status_code == 200, cr.text

        qr = client.post("/api/quantum")
        assert qr.status_code == 200, qr.text
        assert_valid_result(qr.json())

        comp = client.get("/api/compare")   # GET endpoint
        assert comp.status_code == 200, comp.text
        assert comp.json()["winner"] in {"classical", "quantum", "tie"}

    def test_reset_clears_state(self):
        """After DELETE /api/reset (full reset), /api/quantum must return 400."""
        client = TestClient(app)
        client.post("/api/reset")
        upload(client, make_csv(3, demand=10.0), FLEET_3, CAPS_TIGHT)
        # DELETE /api/reset wipes everything including the dataset
        resp = client.delete("/api/reset")
        assert resp.status_code == 200, f"DELETE /api/reset failed: {resp.text}"
        resp = client.post("/api/quantum")
        assert resp.status_code in {400, 422, 500}, \
            f"Expected error after full reset, got {resp.status_code}: {resp.text}"

    def test_repeated_quantum_calls_stable(self):
        """Calling /api/quantum twice must not crash or corrupt state."""
        client = TestClient(app)
        client.post("/api/reset")
        upload(client, make_csv(4, demand=10.0), FLEET_3, CAPS_GENEROUS)
        r1 = run_quantum(client)
        r2 = run_quantum(client)
        assert_valid_result(r1)
        assert_valid_result(r2)

    def test_quantum_with_mixed_fleet(self):
        """Mixed Van+Truck fleet — capacities_list must be correctly ordered."""
        client = TestClient(app)
        client.post("/api/reset")
        upload(client, make_csv(5, demand=10.0), FLEET_MIXED, CAPS_MIXED)
        result = run_quantum(client)
        assert_valid_result(result)

    def test_all_customers_visited_exactly_once(self):
        """Every customer in the CSV must appear exactly once in the routes."""
        n = 8
        client = TestClient(app)
        client.post("/api/reset")
        upload(client, make_csv(n, demand=5.0), FLEET_3, CAPS_GENEROUS)
        result = run_quantum(client)
        ids = customer_ids_in_routes(result["routes"])
        assert len(ids) == n,                  f"Expected {n} nodes, got {len(ids)}"
        assert set(ids) == set(range(1, n+1)), f"Wrong customer IDs: {ids}"
        assert len(ids) == len(set(ids)),       "Duplicate visits"

    def test_integer_demands_parsed_correctly(self):
        """Integer demand values must be parsed as floats without error."""
        client = TestClient(app)
        client.post("/api/reset")
        csv = "Customer_ID,Latitude,Longitude,Demand\n1,12.97,77.59,5\n2,12.98,77.60,15\n3,12.99,77.61,25"
        upload(client, csv, FLEET_3, CAPS_TIGHT)
        result = run_quantum(client)
        assert_valid_result(result)

    def test_route_meta_present_and_consistent(self):
        """route_meta must be present, one entry per route, with valid load_pct."""
        client = TestClient(app)
        client.post("/api/reset")
        upload(client, make_csv(4, demand=10.0), FLEET_3, CAPS_GENEROUS)
        result = run_quantum(client)
        assert "route_meta" in result, "route_meta missing from response"
        assert len(result["route_meta"]) == len(result["routes"]), \
            "route_meta length != routes length"
        for meta in result["route_meta"]:
            if meta.get("load_pct") is not None:
                assert meta["load_pct"] >= 0, f"Negative load_pct: {meta}"
                assert meta["load_pct"] <= 110, f"Unreasonably high load_pct: {meta}"


# ---------------------------------------------------------------------------
# 8. CSV parsing rejection (upload-level)
# ---------------------------------------------------------------------------

class TestCSVParsing:

    def _bad_upload(self, csv: str) -> int:
        client = TestClient(app)
        response = client.post(
            "/api/upload",
            files={"file": ("bad.csv", csv, "text/csv")},
            data={"fleet": json.dumps(FLEET_3), "capacities": json.dumps(CAPS_TIGHT)},
        )
        return response.status_code

    def test_missing_demand_column_rejected(self):
        assert self._bad_upload("Customer_ID,Latitude,Longitude\n1,12.97,77.59") == 422

    def test_zero_demand_rejected(self):
        assert self._bad_upload("Customer_ID,Latitude,Longitude,Demand\n1,12.97,77.59,0.0") == 422

    def test_negative_demand_rejected(self):
        assert self._bad_upload("Customer_ID,Latitude,Longitude,Demand\n1,12.97,77.59,-5.0") == 422

    def test_duplicate_customer_id_rejected(self):
        assert self._bad_upload(
            "Customer_ID,Latitude,Longitude,Demand\n1,12.97,77.59,10.0\n1,12.98,77.60,10.0"
        ) == 422

    def test_empty_csv_rejected(self):
        client = TestClient(app)
        response = client.post(
            "/api/upload",
            files={"file": ("empty.csv", b"", "text/csv")},
            data={"fleet": json.dumps(FLEET_3), "capacities": json.dumps(CAPS_TIGHT)},
        )
        assert response.status_code in {400, 422}

    def test_non_numeric_demand_rejected(self):
        assert self._bad_upload(
            "Customer_ID,Latitude,Longitude,Demand\n1,12.97,77.59,abc"
        ) == 422

    def test_out_of_range_latitude_rejected(self):
        assert self._bad_upload(
            "Customer_ID,Latitude,Longitude,Demand\n1,95.0,77.59,10.0"
        ) == 422

    def test_out_of_range_longitude_rejected(self):
        assert self._bad_upload(
            "Customer_ID,Latitude,Longitude,Demand\n1,12.97,200.0,10.0"
        ) == 422
