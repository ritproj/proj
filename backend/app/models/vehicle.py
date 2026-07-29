from __future__ import annotations

from typing import Dict, List
from pydantic import BaseModel, model_validator

# Fuel rates L/km — single source of truth, keys match frontend labels exactly
VEHICLE_FUEL_RATES: Dict[str, float] = {
    "Van":          0.11,
    "Truck":        0.18,
    "Bike":         0.03,
    "Electric Van": 0.00,
}

# Ordered tuple — deterministic iteration order guaranteed across all Python versions
ALLOWED_VEHICLE_TYPES: tuple = ("Van", "Truck", "Bike", "Electric Van")


class VehicleConfig(BaseModel):
    """
    Fleet configuration with per-type count AND per-type capacity.

    fleet:      { "Van": 2, "Truck": 1, "Bike": 0, "Electric Van": 0 }
    capacities: { "Van": 50, "Truck": 120, "Bike": 15, "Electric Van": 60 }
    """
    fleet:      Dict[str, int]    # type → count  (0 = not used)
    capacities: Dict[str, float]  # type → capacity per vehicle of that type

    @model_validator(mode="after")
    def validate_fleet(self) -> "VehicleConfig":
        allowed_set = set(ALLOWED_VEHICLE_TYPES)
        # All fleet keys must be recognised
        bad_fleet = set(self.fleet) - allowed_set
        if bad_fleet:
            raise ValueError(
                f"Unrecognised vehicle type(s) in fleet: {sorted(bad_fleet)}. "
                f"Allowed: {list(ALLOWED_VEHICLE_TYPES)}"
            )
        # All capacity keys must be recognised
        bad_cap = set(self.capacities) - allowed_set
        if bad_cap:
            raise ValueError(
                f"Unrecognised vehicle type(s) in capacities: {sorted(bad_cap)}. "
                f"Allowed: {list(ALLOWED_VEHICLE_TYPES)}"
            )
        # Every used vehicle type must have a capacity entry
        for vtype, cnt in self.fleet.items():
            if cnt > 0 and vtype not in self.capacities:
                raise ValueError(
                    f"Vehicle type '{vtype}' has {cnt} vehicles but no capacity defined."
                )
        # Counts must be >= 0
        for vtype, cnt in self.fleet.items():
            if cnt < 0:
                raise ValueError(f"Count for '{vtype}' must be >= 0, got {cnt}")
        # Capacities must be positive
        for vtype, cap in self.capacities.items():
            if cap <= 0:
                raise ValueError(f"Capacity for '{vtype}' must be > 0, got {cap}")
        # Total fleet must have at least 1 vehicle
        if self.total_count < 1:
            raise ValueError("Fleet must have at least 1 vehicle in total.")
        return self

    # ── Derived properties ─────────────────────────────────────────────

    @property
    def total_count(self) -> int:
        """Total number of vehicles across all types."""
        return sum(self.fleet.values())

    @property
    def capacities_list(self) -> List[float]:
        """
        Ordered list of capacities, one entry per vehicle slot.
        e.g. fleet={Van:2, Truck:1} → [50, 50, 120]
        Matches the vehicle index used by OR-Tools and QAOA.
        """
        result = []
        for vtype in ALLOWED_VEHICLE_TYPES:  # consistent ordering
            cnt = self.fleet.get(vtype, 0)
            cap = self.capacities.get(vtype, 0.0)
            result.extend([cap] * cnt)
        return result

    @property
    def vehicle_types_list(self) -> List[str]:
        """
        Ordered list of vehicle types, one entry per vehicle slot.
        e.g. fleet={Van:2, Truck:1} → ['Van', 'Van', 'Truck']
        """
        result = []
        for vtype in ALLOWED_VEHICLE_TYPES:
            cnt = self.fleet.get(vtype, 0)
            result.extend([vtype] * cnt)
        return result

    @property
    def blended_fuel_rate(self) -> float:
        """Weighted average fuel rate (L/km) across the whole fleet."""
        total = self.total_count
        if total == 0:
            return 0.0
        return sum(
            VEHICLE_FUEL_RATES[vt] * cnt
            for vt, cnt in self.fleet.items()
            if cnt > 0
        ) / total

    @property
    def dominant_type(self) -> str:
        """The vehicle type with the highest count (for display)."""
        active = {k: v for k, v in self.fleet.items() if v > 0}
        if not active:
            return next(iter(ALLOWED_VEHICLE_TYPES))
        return max(active, key=lambda k: active[k])

    @property
    def max_capacity(self) -> float:
        """Largest single-vehicle capacity in the fleet (used as QUBO bound)."""
        if not self.capacities_list:
            return 0.0
        return max(self.capacities_list)
