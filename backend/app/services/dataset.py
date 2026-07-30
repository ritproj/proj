"""
dataset.py — CSV parsing, validation, and k-means clustering for large datasets.

The depot is NOT in the CSV; it is loaded from depot.json (Option A from spec).
Clustering notice threshold matches the frontend (QUANTUM_CUSTOMER_LIMIT = 8).
"""

from __future__ import annotations

import io
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from app.models.customer import Customer

REQUIRED_COLUMNS = {"Customer_ID", "Latitude", "Longitude", "Demand"}
from app import config as _cfg

def _customer_limit() -> int:
    """Return the correct per-solver customer limit from config."""
    backend = getattr(_cfg, "QUANTUM_SOLVER_BACKEND", "qaoa").lower()
    if backend == "bqphy":
        return getattr(_cfg, "BQPHY_CUSTOMER_LIMIT", 50)
    return getattr(_cfg, "QAOA_CUSTOMER_LIMIT", 8)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_csv(contents: bytes) -> Tuple[List[Customer], bool]:
    """
    Parse and validate a CSV file.

    Returns
    -------
    customers : list[Customer]
        Validated customer objects.
    clustering_notice : bool
        True when the dataset exceeds QUANTUM_CUSTOMER_LIMIT and will be
        clustered before QUBO/QAOA runs.

    Raises
    ------
    ValueError
        On missing columns, invalid values, or empty data.
    """
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as exc:
        raise ValueError(f"Could not parse CSV: {exc}") from exc

    # --- Column check ---
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df[list(REQUIRED_COLUMNS)].copy()

    # --- Empty check ---
    if len(df) == 0:
        raise ValueError("CSV contains no data rows.")

    # --- Type coercion ---
    for col in ("Latitude", "Longitude", "Demand"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df[["Latitude", "Longitude", "Demand"]].isnull().any().any():
        bad = df[df[["Latitude", "Longitude", "Demand"]].isnull().any(axis=1)]["Customer_ID"].tolist()
        raise ValueError(f"Non-numeric values in row(s) for Customer_ID: {bad}")

    # --- Demand > 0 ---
    bad_demand = df[df["Demand"] <= 0]["Customer_ID"].tolist()
    if bad_demand:
        raise ValueError(f"Demand must be > 0 for Customer_ID(s): {bad_demand}")

    # --- Lat / Lon range ---
    bad_lat = df[(df["Latitude"] < -90) | (df["Latitude"] > 90)]["Customer_ID"].tolist()
    if bad_lat:
        raise ValueError(f"Latitude out of range [-90, 90] for Customer_ID(s): {bad_lat}")

    bad_lon = df[(df["Longitude"] < -180) | (df["Longitude"] > 180)]["Customer_ID"].tolist()
    if bad_lon:
        raise ValueError(f"Longitude out of range [-180, 180] for Customer_ID(s): {bad_lon}")

    # --- Duplicate Customer_ID check ---
    if df["Customer_ID"].duplicated().any():
        dup_ids = sorted(df["Customer_ID"][df["Customer_ID"].duplicated(keep=False)].unique().tolist())
        raise ValueError(f"Duplicate Customer_ID(s) found: {dup_ids}. Each customer must have a unique ID.")

    customers: List[Customer] = [
        Customer(
            customer_id=int(row["Customer_ID"]),
            latitude=float(row["Latitude"]),
            longitude=float(row["Longitude"]),
            demand=float(row["Demand"]),
        )
        for _, row in df.iterrows()
    ]

    clustering_notice = len(customers) > _customer_limit()
    return customers, clustering_notice


def cluster_customers(
    customers: List[Customer],
    n_clusters: int,
) -> List[List[Customer]]:
    """
    Split customers into n_clusters groups using k-means on (lat, lon).
    Each cluster is then solved as an independent CVRP sub-problem.

    Returns a list of customer lists (one per cluster).
    """
    if len(customers) <= n_clusters:
        # Trivial: one customer per cluster
        return [[c] for c in customers]

    coords = np.array([[c.latitude, c.longitude] for c in customers])
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    labels = km.fit_predict(coords)

    clusters: List[List[Customer]] = [[] for _ in range(n_clusters)]
    for customer, label in zip(customers, labels):
        clusters[label].append(customer)

    # Drop empty clusters
    return [cl for cl in clusters if cl]
