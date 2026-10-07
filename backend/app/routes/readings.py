from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.reading import BatteryReading
from app.schemas.reading import ReadingCreate, ReadingResponse
from app.services.battery_service import find_battery, get_readings
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/api/batteries",
    tags=["Battery Readings"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/{battery_id}/readings", response_model=ReadingResponse, status_code=201)
def create_reading(
    battery_id: str,
    reading: ReadingCreate,
    db: Session = Depends(get_db),
):
    battery = find_battery(db, battery_id)
    new_reading = BatteryReading(
        battery_id=battery.id,
        **reading.model_dump(),
    )
    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)
    return new_reading


@router.get("/{battery_id}/readings", response_model=list[ReadingResponse])
def list_readings(battery_id: str, db: Session = Depends(get_db)):
    battery = find_battery(db, battery_id)
    return get_readings(db, battery)
