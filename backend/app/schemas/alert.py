from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AlertCreate(BaseModel):
    battery_id: str | None = Field(default=None, max_length=50)
    alert_type: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    battery_id: int | None
    alert_type: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime


class WhatIfRequest(BaseModel):
    temperature: float | None = None
    measured_capacity: float | None = Field(default=None, gt=0)
    cycle_count: int | None = Field(default=None, ge=0)
