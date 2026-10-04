from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from datetime import datetime

from app.database.base import Base


class BatteryReading(Base):
    __tablename__ = "battery_readings"

    id = Column(Integer, primary_key=True, index=True)

    battery_id = Column(
        Integer,
        ForeignKey("batteries.id"),
        nullable=False
    )

    voltage = Column(
        Float,
        nullable=False
    )

    current = Column(
        Float,
        nullable=False
    )

    temperature = Column(
        Float,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )