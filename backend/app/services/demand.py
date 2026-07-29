"""
demand.py — lightweight pre-flight fleet capacity check (backend_v2 §6.1).

Called right after upload validation; does not block the pipeline — it only
surfaces an honest warning so the user knows before a solver run whether their
fleet is undersized.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from app.models.customer import Customer
from app.models.vehicle import VehicleConfig


def check_fleet_capacity(
    customers: List[Customer],
    vehicle_config: VehicleConfig,
) -> Dict:
    """
    Compare total customer demand against total fleet capacity.

    Returns
    -------
    dict with keys:
        total_demand       : float   — sum of all customer demands
        total_capacity     : float   — sum of capacities_list (per-slot)
        sufficient         : bool    — total_capacity >= total_demand
        utilization_pct    : float | None — demand/capacity × 100
        warning            : str | None  — human-readable alert when !sufficient
    """
    total_demand: float   = sum(c.demand for c in customers)
    total_capacity: float = sum(vehicle_config.capacities_list)

    if total_capacity <= 0:
        return {
            "total_demand":    round(total_demand, 2),
            "total_capacity":  0.0,
            "sufficient":      False,
            "utilization_pct": None,
            "warning":         "Fleet has zero total capacity — add at least one vehicle.",
        }

    utilization_pct = round(total_demand / total_capacity * 100, 1)
    sufficient      = total_capacity >= total_demand

    warning: Optional[str] = None
    if not sufficient:
        shortage = round(total_demand - total_capacity, 1)
        warning = (
            f"Fleet capacity ({total_capacity:.0f} kg) is less than total demand "
            f"({total_demand:.0f} kg) by {shortage} kg — "
            f"OR-Tools and QAOA will fail to find a feasible solution. "
            f"Increase vehicle count or capacity before running optimisation."
        )

    return {
        "total_demand":    round(total_demand, 2),
        "total_capacity":  round(total_capacity, 2),
        "sufficient":      sufficient,
        "utilization_pct": utilization_pct,
        "warning":         warning,
    }
