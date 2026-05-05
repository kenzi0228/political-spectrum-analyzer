from __future__ import annotations

from typing import Dict

from political_spectrum_analyzer.constants import VARIABLE_NAMES


def validate_scores(scores: Dict[str, int]) -> None:
    missing = [name for name in VARIABLE_NAMES if name not in scores]
    if missing:
        raise ValueError(f"Missing score(s): {', '.join(missing)}")

    for key, value in scores.items():
        if key not in VARIABLE_NAMES:
            raise ValueError(f"Unknown score key: {key}")
        if not isinstance(value, int):
            raise ValueError(f"Score '{key}' must be an integer.")
        if not (0 <= value <= 100):
            raise ValueError(f"Score '{key}' must be between 0 and 100.")