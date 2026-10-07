from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database.base import Base


class Battery(Base):
    __tablename__ = "batteries"

    id = Column(Integer, primary_key=True, index=True)

    battery_id = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    battery_type = Column(
        String(100),
        nullable=True
    )

    capacity = Column(
        Float,
        nullable=True
    )

    status = Column(
        String(50),
        default="Active"
    )

    serial_number = Column(String(100), nullable=True)
    manufacturer = Column(String(150), nullable=True)
    chemistry = Column(String(100), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )