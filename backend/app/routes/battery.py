import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.decision_engine.reassessment import get_second_life_recommendations
from app.database.connection import get_db
from app.models.assessment import Assessment
from app.models.battery import Battery
from app.schemas.alert import WhatIfRequest
from app.schemas.battery import BatteryCreate, BatteryResponse, BatteryUpdate
from app.services.assessment_service import assess_battery
from app.services.battery_service import find_battery, get_readings
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/api/batteries",
    tags=["Batteries"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=BatteryResponse, status_code=201)
def create_battery(battery: BatteryCreate, db: Session = Depends(get_db)):
    new_battery = Battery(**battery.model_dump())
    db.add(new_battery)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="battery_id already exists") from None
    db.refresh(new_battery)
    return new_battery


@router.get("", response_model=list[BatteryResponse])
def list_batteries(db: Session = Depends(get_db)):
    return db.query(Battery).order_by(Battery.id).all()


@router.get("/{battery_id}", response_model=BatteryResponse)
def read_battery(battery_id: str, db: Session = Depends(get_db)):
    return find_battery(db, battery_id)


@router.put("/{battery_id}", response_model=BatteryResponse)
def update_battery(
    battery_id: str,
    changes: BatteryUpdate,
    db: Session = Depends(get_db),
):
    battery = find_battery(db, battery_id)
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(battery, field, value)
    db.commit()
    db.refresh(battery)
    return battery


def _assessment(db: Session, battery: Battery):
    return assess_battery(battery, get_readings(db, battery))


@router.get("/{battery_id}/soh")
def get_soh(battery_id: str, db: Session = Depends(get_db)):
    result = _assessment(db, find_battery(db, battery_id))
    return {"battery_id": battery_id, "soh": result.soh, "method": result.method}


@router.get("/{battery_id}/rul")
def get_rul(battery_id: str, db: Session = Depends(get_db)):
    result = _assessment(db, find_battery(db, battery_id))
    return {
        "battery_id": battery_id,
        "rul_cycles": result.rul_cycles,
        "unit": "cycles",
        "method": result.method,
    }


@router.get("/{battery_id}/prediction")
def get_prediction(battery_id: str, db: Session = Depends(get_db)):
    result = _assessment(db, find_battery(db, battery_id))
    return {
        "battery_id": battery_id,
        "soh": result.soh,
        "rul_cycles": result.rul_cycles,
        "decision": result.decision,
        "method": result.method,
        "explanation": result.explanation,
    }


@router.get("/{battery_id}/decision")
def get_decision(battery_id: str, db: Session = Depends(get_db)):
    result = _assessment(db, find_battery(db, battery_id))
    return {"battery_id": battery_id, "decision": result.decision, "soh": result.soh}


@router.get("/{battery_id}/decision/why")
def get_decision_explanation(battery_id: str, db: Session = Depends(get_db)):
    result = _assessment(db, find_battery(db, battery_id))
    return {
        "battery_id": battery_id,
        "decision": result.decision,
        "soh": result.soh,
        "reasons": result.explanation,
        "method": result.method,
    }


@router.get("/{battery_id}/second-life")
def get_second_life_recommendation(battery_id: str, db: Session = Depends(get_db)):
    result = _assessment(db, find_battery(db, battery_id))
    return {
        "battery_id": battery_id,
        "decision": result.decision,
        "soh": result.soh,
        "recommendations": get_second_life_recommendations(result.decision),
    }


@router.post("/{battery_id}/what-if")
def what_if(
    battery_id: str,
    changes: WhatIfRequest,
    db: Session = Depends(get_db),
):
    battery = find_battery(db, battery_id)
    result = assess_battery(
        battery,
        get_readings(db, battery),
        temperature=changes.temperature,
        measured_capacity=changes.measured_capacity,
        cycle_count=changes.cycle_count,
    )
    return {
        "battery_id": battery_id,
        "scenario": changes.model_dump(exclude_unset=True),
        "soh": result.soh,
        "rul_cycles": result.rul_cycles,
        "decision": result.decision,
        "method": result.method,
        "explanation": result.explanation,
        "persisted": False,
    }


@router.post("/{battery_id}/reassessment")
def reassess_battery(battery_id: str, db: Session = Depends(get_db)):
    battery = find_battery(db, battery_id)
    result = _assessment(db, battery)
    assessment = Assessment(
        battery_id=battery.id,
        soh=result.soh,
        rul_cycles=result.rul_cycles,
        decision=result.decision,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return {
        "assessment_id": assessment.id,
        "battery_id": battery_id,
        "soh": result.soh,
        "rul_cycles": result.rul_cycles,
        "decision": result.decision,
        "assessed_at": assessment.assessed_at,
    }


@router.get("/{battery_id}/passport")
def get_battery_passport(battery_id: str, db: Session = Depends(get_db)):
    battery = find_battery(db, battery_id)
    result = assess_battery(battery, get_readings(db, battery))
    passport_data = {
        "battery_id": battery.battery_id,
        "battery_type": battery.battery_type,
        "capacity": battery.capacity,
        "manufacturer": battery.manufacturer,
        "chemistry": battery.chemistry,
        "serial_number": battery.serial_number,
        "status": battery.status,
        "soh": result.soh,
        "decision": result.decision,
    }
    return {
        **passport_data,
        "qr_payload": json.dumps(passport_data, separators=(",", ":")),
    }


@router.get("/{battery_id}/history")
def get_battery_history(battery_id: str, db: Session = Depends(get_db)):
    battery = find_battery(db, battery_id)
    readings = get_readings(db, battery)
    history = []
    for reading in reversed(readings):
        result = assess_battery(battery, [reading])
        history.append({
            "reading_id": reading.id,
            "timestamp": reading.timestamp,
            "voltage": reading.voltage,
            "current": reading.current,
            "temperature": reading.temperature,
            "measured_capacity": reading.measured_capacity,
            "cycle_count": reading.cycle_count,
            "soh": result.soh,
        })
    return {"battery_id": battery_id, "history": history}
