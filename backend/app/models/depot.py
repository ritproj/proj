from pydantic import BaseModel, field_validator


class Depot(BaseModel):
    depot_id: int = 0
    latitude: float
    longitude: float

    @field_validator("latitude")
    @classmethod
    def latitude_range(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError(f"Depot latitude must be in [-90, 90], got {v}")
        return v

    @field_validator("longitude")
    @classmethod
    def longitude_range(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError(f"Depot longitude must be in [-180, 180], got {v}")
        return v
