from pydantic import BaseModel


class BatteryCreate(BaseModel):
    battery_id: str
    battery_type: str | None = None
    capacity: float | None = None