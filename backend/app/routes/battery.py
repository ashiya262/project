from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.battery import Battery
from app.schemas.battery import BatteryCreate


router = APIRouter(prefix="/batteries", tags=["Batteries"])


@router.post("")
def create_battery(
    battery: BatteryCreate,
    db: Session = Depends(get_db)
):
    new_battery = Battery(
        battery_id=battery.battery_id,
        battery_type=battery.battery_type,
        capacity=battery.capacity
    )

    db.add(new_battery)
    db.commit()
    db.refresh(new_battery)

    return {
        "message": "Battery created successfully",
        "battery_id": new_battery.battery_id
    }

@router.get("/")
def get_batteries(
    db: Session = Depends(get_db)
):
    batteries = db.query(Battery).all()

    return batteries