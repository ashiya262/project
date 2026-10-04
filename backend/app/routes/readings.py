from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.reading import BatteryReading
from app.schemas.reading import ReadingCreate


router = APIRouter(
    prefix="/readings",
    tags=["Battery Readings"]
)


@router.post("/")
def create_reading(
    reading: ReadingCreate,
    db: Session = Depends(get_db)
):
    new_reading = BatteryReading(
        battery_id=reading.battery_id,
        voltage=reading.voltage,
        current=reading.current,
        temperature=reading.temperature
    )

    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    return {
        "message": "Battery reading saved successfully",
        "reading_id": new_reading.id
    }
@router.get("/")
def get_readings(
    db: Session = Depends(get_db)
):
    readings = db.query(BatteryReading).all()

    return readings
