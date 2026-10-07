from dataclasses import dataclass

from app.models.battery import Battery
from app.models.reading import BatteryReading


@dataclass(frozen=True)
class BatteryAssessment:
    soh: float
    rul_cycles: int
    decision: str
    latest_reading: BatteryReading | None
    explanation: list[str]
    method: str


def assess_battery(
    battery: Battery,
    readings: list[BatteryReading],
    *,
    temperature: float | None = None,
    measured_capacity: float | None = None,
    cycle_count: int | None = None,
) -> BatteryAssessment:
    latest = readings[0] if readings else None
    temp = temperature if temperature is not None else (latest.temperature if latest else 25.0)
    actual_capacity = (
        measured_capacity
        if measured_capacity is not None
        else (latest.measured_capacity if latest else None)
    )
    cycles = cycle_count if cycle_count is not None else (latest.cycle_count if latest else None)

    explanation: list[str] = []
    if actual_capacity is not None and battery.capacity and battery.capacity > 0:
        soh = min(100.0, max(0.0, actual_capacity / battery.capacity * 100))
        method = "measured_capacity"
        explanation.append("SOH is calculated from the latest measured capacity and rated capacity.")
    else:
        cycle_degradation = max(0, cycles or 0) * 0.02
        temperature_degradation = max(0.0, temp - 25.0) * 0.3
        soh = min(100.0, max(0.0, 100.0 - cycle_degradation - temperature_degradation))
        method = "rule_based_estimate"
        explanation.append(
            "SOH is an estimate based on cycle count and temperature; provide measured_capacity "
            "and rated battery capacity for a capacity-based result."
        )

    if temp > 45:
        explanation.append("High temperature is increasing battery risk.")
    if cycles is not None and cycles >= 500:
        explanation.append("The reported cycle count indicates significant battery use.")

    rul_cycles = max(0, round(max(0.0, soh - 60.0) * 20))
    if soh >= 80:
        decision = "EV"
        explanation.append("SOH is at least 80%, so continued EV use is recommended.")
    elif soh >= 65:
        decision = "SOLAR_STORAGE"
        explanation.append("SOH is suitable for stationary solar energy storage.")
    elif soh >= 50:
        decision = "UPS"
        explanation.append("SOH is below the solar-storage range; limited UPS use is suggested.")
    else:
        decision = "RECYCLING"
        explanation.append("SOH is below 50%, so recycling is recommended.")

    return BatteryAssessment(
        soh=round(soh, 2),
        rul_cycles=rul_cycles,
        decision=decision,
        latest_reading=latest,
        explanation=explanation,
        method=method,
    )
