"""Pydantic schemas for request validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class TankCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    water_type: str = Field(default="freshwater", pattern="^(freshwater|planted|shrimp)$")


class ReadingCreate(BaseModel):
    tank_id: int = Field(gt=0)
    ph: Optional[float] = Field(default=None, ge=0, le=14)
    temperature_c: Optional[float] = Field(default=None, ge=-10, le=60)
    nh3_ppm: Optional[float] = Field(default=None, ge=0, le=500)
    no2_ppm: Optional[float] = Field(default=None, ge=0, le=500)
    no3_ppm: Optional[float] = Field(default=None, ge=0, le=1000)
    measured_at: Optional[datetime] = None

    @model_validator(mode="after")
    def at_least_one_value(self):
        if all(
            v is None
            for v in (self.ph, self.temperature_c, self.nh3_ppm, self.no2_ppm, self.no3_ppm)
        ):
            raise ValueError("at least one parameter value is required")
        return self
