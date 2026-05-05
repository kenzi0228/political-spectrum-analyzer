from __future__ import annotations

import math
from typing import Dict, Tuple


def _safe_get(scores: Dict[str, int], key: str) -> float:
    return float(scores.get(key, 0))


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def _sigmoid_scaled(value: float, scale: float = 1.0) -> float:
    """
    Smooth non-linear compression to avoid extreme jumps.
    Returns a value roughly bounded in [-1, 1].
    """
    z = value / scale
    return 2.0 / (1.0 + math.exp(-z)) - 1.0


def apply_transformations_and_get_coordinates(scores: Dict[str, int]) -> Tuple[float, float]:
    """
    Convert 16 ideological dimensions into 2D political coordinates.

    X axis:
        negative -> economically left
        positive -> economically right

    Y axis:
        negative -> libertarian / socially progressive
        positive -> authoritarian / socially conservative
    """

    # =========================
    # Economic axis components
    # =========================
    left_economic = (
        0.90 * _safe_get(scores, "communisme")
        + 0.75 * _safe_get(scores, "regulation")
        + 0.35 * _safe_get(scores, "ecologie")
        + 0.25 * _safe_get(scores, "revolution")
    )

    right_economic = (
        0.90 * _safe_get(scores, "capitalisme")
        + 0.75 * _safe_get(scores, "laissez_faire")
        + 0.35 * _safe_get(scores, "productivisme")
        + 0.20 * _safe_get(scores, "reformisme")
    )

    # =========================
    # Societal axis components
    # =========================
    libertarian_social = (
        0.75 * _safe_get(scores, "constructivisme")
        + 0.70 * _safe_get(scores, "justice_rehabilitative")
        + 0.70 * _safe_get(scores, "progressisme")
        + 0.55 * _safe_get(scores, "internationalisme")
    )

    authoritarian_social = (
        0.75 * _safe_get(scores, "essentialisme")
        + 0.70 * _safe_get(scores, "justice_punitive")
        + 0.70 * _safe_get(scores, "conservatisme")
        + 0.55 * _safe_get(scores, "nationalisme")
    )

    # =========================
    # Secondary interactions
    # =========================
    economic_raw = right_economic - left_economic
    societal_raw = authoritarian_social - libertarian_social

    # Additional nuance: productivism and ecology can slightly sharpen
    # economic and societal interpretation.
    economic_raw += 0.12 * (_safe_get(scores, "productivisme") - _safe_get(scores, "ecologie"))
    societal_raw += 0.10 * (_safe_get(scores, "nationalisme") - _safe_get(scores, "internationalisme"))

    # Revolution/reformism can affect political posture slightly
    societal_raw += 0.08 * (_safe_get(scores, "revolution") - _safe_get(scores, "reformisme"))

    # =========================
    # Normalize and compress
    # =========================
    # Typical raw range is a few hundred points, so divide first
    economic_normalized = economic_raw / 120.0
    societal_normalized = societal_raw / 120.0

    x = 4.0 * _sigmoid_scaled(economic_normalized, scale=1.0)
    y = 4.0 * _sigmoid_scaled(societal_normalized, scale=1.0)

    x = _clamp(x, -4.0, 4.0)
    y = _clamp(y, -4.0, 4.0)

    return x, y