from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from app.database.base import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    battery_id = Column(Integer, ForeignKey("batteries.id"), nullable=False, index=True)
    soh = Column(Float, nullable=False)
    rul_cycles = Column(Integer, nullable=False)
    decision = Column(String(30), nullable=False)
    assessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
