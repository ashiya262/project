SECOND_LIFE_RECOMMENDATIONS: dict[str, list[str]] = {
    "EV": ["EV continued use", "solar storage"],
    "SOLAR_STORAGE": ["solar storage", "stationary energy storage"],
    "UPS": ["UPS backup", "low-demand stationary storage"],
    "RECYCLING": ["certified battery recycling"],
}


def get_second_life_recommendations(decision: str) -> list[str]:
    """Return suitable destinations for a battery assessment decision."""
    try:
        return SECOND_LIFE_RECOMMENDATIONS[decision].copy()
    except KeyError:
        raise ValueError(f"Unsupported battery decision: {decision}") from None