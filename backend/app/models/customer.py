from pydantic import BaseModel, field_validator


class Customer(BaseModel):
    customer_id: int
    latitude: float
    longitude: float
    demand: float

    @field_validator("demand")
    @classmethod
    def demand_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"Demand must be > 0, got {v}")
        return v

    @field_validator("latitude")
    @classmethod
    def latitude_range(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError(f"Latitude must be in [-90, 90], got {v}")
        return v

    @field_validator("longitude")
    @classmethod
    def longitude_range(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError(f"Longitude must be in [-180, 180], got {v}")
        return v
