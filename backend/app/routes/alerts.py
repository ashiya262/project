from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertResponse
from app.services.battery_service import find_battery
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/api",
    tags=["Alerts"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.created_at.desc()).all()


@router.get("/batteries/{battery_id}/alerts", response_model=list[AlertResponse])
def list_battery_alerts(battery_id: str, db: Session = Depends(get_db)):
    battery = find_battery(db, battery_id)
    return (
        db.query(Alert)
        .filter(Alert.battery_id == battery.id)
        .order_by(Alert.created_at.desc())
        .all()
    )


@router.post("/alerts", response_model=AlertResponse, status_code=201)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    internal_battery_id = None
    if payload.battery_id is not None:
        internal_battery_id = find_battery(db, payload.battery_id).id
    alert = Alert(
        battery_id=internal_battery_id,
        alert_type=payload.alert_type,
        message=payload.message,
        severity=payload.severity,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.put("/alerts/{alert_id}/read", response_model=AlertResponse)
def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return alert
