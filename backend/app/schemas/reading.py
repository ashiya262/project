from pydantic import BaseModel


class ReadingCreate(BaseModel):
    battery_id: int
    voltage: float
    current: float
    temperature: float