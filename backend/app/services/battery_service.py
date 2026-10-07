from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.battery import Battery
from app.models.reading import BatteryReading


def find_battery(db: Session, battery_id: str) -> Battery:
    lookup_id = battery_id.strip().strip("\"'").strip()
    battery = db.query(Battery).filter(Battery.battery_id == lookup_id).first()
    if battery is None and lookup_id.isdecimal():
        battery = db.query(Battery).filter(Battery.id == int(lookup_id)).first()
    if battery is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Battery not found. Use the battery_id or numeric id returned "
                f"by GET /api/batteries (received: {lookup_id})."
            ),
        )
    return battery


def get_readings(db: Session, battery: Battery) -> list[BatteryReading]:
    return (
        db.query(BatteryReading)
        .filter(BatteryReading.battery_id == battery.id)
        .order_by(BatteryReading.timestamp.desc(), BatteryReading.id.desc())
        .all()
    )
