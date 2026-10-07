from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.alert import Alert
from app.models.battery import Battery
from app.models.reading import BatteryReading
from app.services.assessment_service import assess_battery
from app.services.battery_service import get_readings
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/api",
    tags=["Dashboard and Analytics"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    batteries = db.query(Battery).all()
    decisions = {"EV": 0, "SOLAR_STORAGE": 0, "UPS": 0, "RECYCLING": 0}
    soh_values = []
    for battery in batteries:
        result = assess_battery(battery, get_readings(db, battery))
        decisions[result.decision] += 1
        soh_values.append(result.soh)
    unread_alerts = db.query(Alert).filter(Alert.is_read.is_(False)).count()
    return {
        "battery_count": len(batteries),
        "average_soh": round(sum(soh_values) / len(soh_values), 2) if soh_values else None,
        "unread_alert_count": unread_alerts,
        "decisions": decisions,
    }


@router.get("/analytics/soh")
def analytics_soh(db: Session = Depends(get_db)):
    results = []
    for battery in db.query(Battery).order_by(Battery.id).all():
        readings = get_readings(db, battery)
        if readings:
            result = assess_battery(battery, readings)
            results.append({
                "battery_id": battery.battery_id,
                "timestamp": readings[0].timestamp,
                "soh": result.soh,
                "method": result.method,
            })
    return {"data": results}


def _reading_analytics(db: Session, field: str):
    column = getattr(BatteryReading, field)
    rows = (
        db.query(BatteryReading, Battery.battery_id)
        .join(Battery, Battery.id == BatteryReading.battery_id)
        .order_by(BatteryReading.timestamp.asc())
        .all()
    )
    return {
        "data": [
            {
                "battery_id": battery_id,
                "timestamp": reading.timestamp,
                field: getattr(reading, field),
            }
            for reading, battery_id in rows
        ]
    }


@router.get("/analytics/temperature")
def analytics_temperature(db: Session = Depends(get_db)):
    return _reading_analytics(db, "temperature")


@router.get("/analytics/voltage")
def analytics_voltage(db: Session = Depends(get_db)):
    return _reading_analytics(db, "voltage")
