from __future__ import annotations

from typing import Dict, Tuple


PLOT_MIN = -4.0
PLOT_MAX = 4.0


ECONOMIC_LEFT_WEIGHTS = {
    "communisme": 1.00,
    "regulation": 0.75,
    "ecologie": 0.30,
}

ECONOMIC_RIGHT_WEIGHTS = {
    "capitalisme": 1.00,
    "laissez_faire": 0.75,
    "productivisme": 0.30,
}

SOCIETAL_LIBERTARIAN_WEIGHTS = {
    "constructivisme": 0.65,
    "justice_rehabilitative": 0.75,
    "progressisme": 0.80,
    "internationalisme": 0.55,
}

SOCIETAL_AUTHORITARIAN_WEIGHTS = {
    "essentialisme": 0.65,
    "justice_punitive": 0.75,
    "conservatisme": 0.80,
    "nationalisme": 0.55,
}


def _safe_get(scores: Dict[str, int], key: str) -> float:
    return float(scores.get(key, 0))


def _weighted_sum(scores: Dict[str, int], weights: Dict[str, float]) -> float:
    return sum(_safe_get(scores, key) * weight for key, weight in weights.items())


def _clamp(value: float, lower: float = PLOT_MIN, upper: float = PLOT_MAX) -> float:
    return max(lower, min(value, upper))


def _scale_to_axis(raw_difference: float, max_theoretical_difference: float) -> float:
    """
    Convert a raw weighted difference into a [-4, 4] axis.

    Example:
    - raw_difference > 0 pushes the point to the positive side
    - raw_difference < 0 pushes the point to the negative side
    """
    if max_theoretical_difference == 0:
        return 0.0

    return _clamp((raw_difference / max_theoretical_difference) * 4.0)


def compute_radicality(scores: Dict[str, int]) -> float:
    """
    Estimate political radicality from revolution vs reformism.

    Returns a value in [-1, 1]:
    - positive: more revolutionary / rupture-oriented
    - negative: more reformist / institutional
    """
    revolution = _safe_get(scores, "revolution")
    reformism = _safe_get(scores, "reformisme")

    return max(-1.0, min(1.0, (revolution - reformism) / 100.0))


def apply_transformations_and_get_coordinates(scores: Dict[str, int]) -> Tuple[float, float]:
    """
    Convert Politiscales-like ideological scores into 2D coordinates.

    X axis:
        negative -> economically left
        positive -> economically right

    Y axis:
        negative -> libertarian / progressive
        positive -> authoritarian / conservative
    """

    economic_left = _weighted_sum(scores, ECONOMIC_LEFT_WEIGHTS)
    economic_right = _weighted_sum(scores, ECONOMIC_RIGHT_WEIGHTS)

    societal_libertarian = _weighted_sum(scores, SOCIETAL_LIBERTARIAN_WEIGHTS)
    societal_authoritarian = _weighted_sum(scores, SOCIETAL_AUTHORITARIAN_WEIGHTS)

    economic_raw = economic_right - economic_left
    societal_raw = societal_authoritarian - societal_libertarian

    max_economic_difference = 100.0 * max(
        sum(ECONOMIC_LEFT_WEIGHTS.values()),
        sum(ECONOMIC_RIGHT_WEIGHTS.values()),
    )

    max_societal_difference = 100.0 * max(
        sum(SOCIETAL_LIBERTARIAN_WEIGHTS.values()),
        sum(SOCIETAL_AUTHORITARIAN_WEIGHTS.values()),
    )

    x = _scale_to_axis(economic_raw, max_economic_difference)
    y = _scale_to_axis(societal_raw, max_societal_difference)

    return x, y