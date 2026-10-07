from pydantic import BaseModel, ConfigDict, Field


class BatteryCreate(BaseModel):
    battery_id: str = Field(min_length=1, max_length=50)
    battery_type: str | None = Field(default=None, max_length=100)
    capacity: float | None = Field(default=None, gt=0)
    serial_number: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=150)
    chemistry: str | None = Field(default=None, max_length=100)


class BatteryUpdate(BaseModel):
    battery_type: str | None = Field(default=None, max_length=100)
    capacity: float | None = Field(default=None, gt=0)
    status: str | None = Field(default=None, max_length=50)
    serial_number: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=150)
    chemistry: str | None = Field(default=None, max_length=100)


class BatteryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    battery_id: str
    battery_type: str | None
    capacity: float | None
    status: str | None
    serial_number: str | None
    manufacturer: str | None
    chemistry: str | None