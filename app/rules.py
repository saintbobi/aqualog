"""Rule-based water parameter assessment per tank type.

Thresholds follow commonly accepted aquarium keeping guidelines.
Each parameter maps to: (min_safe, max_safe, min_warn, max_warn) —
reading inside safe range -> "ok", inside warn range -> "warning",
outside -> "danger". None means unbounded on that side.
"""

RANGES = {
    "freshwater": {
        "ph":            (6.0, 8.0, 5.5, 8.5),
        "temperature_c": (20.0, 28.0, 18.0, 30.0),
        "nh3_ppm":       (None, 0.02, None, 0.05),
        "no2_ppm":       (None, 0.1, None, 0.3),
        "no3_ppm":       (None, 40.0, None, 80.0),
    },
    "planted": {
        "ph":            (6.0, 7.5, 5.5, 8.0),
        "temperature_c": (22.0, 28.0, 20.0, 30.0),
        "nh3_ppm":       (None, 0.02, None, 0.05),
        "no2_ppm":       (None, 0.1, None, 0.3),
        "no3_ppm":       (5.0, 30.0, 0.0, 50.0),
    },
    "shrimp": {
        "ph":            (6.5, 7.5, 6.0, 8.0),
        "temperature_c": (20.0, 26.0, 18.0, 28.0),
        "nh3_ppm":       (None, 0.01, None, 0.02),
        "no2_ppm":       (None, 0.05, None, 0.1),
        "no3_ppm":       (None, 20.0, None, 40.0),
    },
}

PARAM_LABELS = {
    "ph": "pH",
    "temperature_c": "temperature",
    "nh3_ppm": "NH3",
    "no2_ppm": "NO2",
    "no3_ppm": "NO3",
}


def _judge(value, safe_lo, safe_hi, warn_lo, warn_hi):
    if value is None:
        return None
    if safe_lo is not None and value < safe_lo:
        return "warning" if warn_lo is not None and value >= warn_lo else "danger"
    if safe_hi is not None and value > safe_hi:
        return "warning" if warn_hi is not None and value <= warn_hi else "danger"
    return "ok"


def evaluate(reading: dict, water_type: str) -> dict:
    """Return per-parameter verdicts plus overall status for a reading."""
    ranges = RANGES.get(water_type, RANGES["freshwater"])
    params = {}
    worst = "ok"
    rank = {"ok": 0, "warning": 1, "danger": 2}

    for key, (safe_lo, safe_hi, warn_lo, warn_hi) in ranges.items():
        verdict = _judge(reading.get(key), safe_lo, safe_hi, warn_lo, warn_hi)
        if verdict is not None:
            params[key] = verdict
            if rank[verdict] > rank[worst]:
                worst = verdict

    if worst == "ok" and not params:
        worst = "unknown"

    messages = {
        "safe": "All logged parameters are in the safe range for this tank type.",
        "warning": "Some parameters are drifting out of range — keep monitoring.",
        "danger": "One or more parameters are outside the safe range — act now (water change, check filter).",
        "unknown": "No parameter values logged.",
    }
    overall = {
        "ok": "safe",
        "warning": "warning",
        "danger": "danger",
        "unknown": "unknown",
    }[worst]

    return {
        "status": overall,
        "message": messages[overall],
        "params": params,
    }
