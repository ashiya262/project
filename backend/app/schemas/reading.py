from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReadingCreate(BaseModel):
    voltage: float
    current: float
    temperature: float
    measured_capacity: float | None = Field(default=None, gt=0)
    cycle_count: int | None = Field(default=None, ge=0)


class ReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    battery_id: int
    voltage: float
    current: float
    temperature: float
    measured_capacity: float | None
    cycle_count: int | None
    timestamp: datetime