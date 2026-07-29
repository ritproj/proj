"""
emission.py — fuel consumption, CO₂ emissions, and sustainability savings.

Fuel rate is now computed from the blended fleet rate (VehicleConfig.blended_fuel_rate)
so mixed fleets (e.g. 2 Vans + 1 Truck) get an accurate weighted average.
"""

from __future__ import annotations

from typing import Dict

# Re-export for other modules that still reference VEHICLE_FUEL_RATES directly
from app.models.vehicle import VEHICLE_FUEL_RATES

# kg CO₂ per litre of petrol (IPCC / DEFRA standard)
CO2_EMISSION_FACTOR_KG_PER_L: float = 2.31


def fuel_consumption(distance_km: float, fuel_rate: float) -> float:
    """
    Calculate fuel consumed in litres.

    Parameters
    ----------
    distance_km : total route distance in km
    fuel_rate   : L/km — use VehicleConfig.blended_fuel_rate
    """
    return round(distance_km * fuel_rate, 4)


def co2_emissions(fuel_litres: float) -> float:
    """Calculate CO₂ in kg from fuel consumed (litres)."""
    return round(fuel_litres * CO2_EMISSION_FACTOR_KG_PER_L, 4)


def compute_savings(
    classical_distance: float,
    quantum_distance: float,
    classical_fuel: float,
    quantum_fuel: float,
    classical_co2: float,
    quantum_co2: float,
) -> Dict[str, float]:
    """
    Compute relative savings of quantum vs classical (positive = quantum wins).
    Returns dict with keys: distance_pct, fuel_pct, co2_pct
    """
    def _pct(classical: float, quantum: float) -> float:
        if classical == 0:
            return 0.0
        return round((classical - quantum) / classical * 100, 2)

    return {
        "distance_pct": _pct(classical_distance, quantum_distance),
        "fuel_pct":      _pct(classical_fuel,    quantum_fuel),
        "co2_pct":       _pct(classical_co2,     quantum_co2),
    }
