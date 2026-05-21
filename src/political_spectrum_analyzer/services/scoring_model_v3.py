"""Scoring model v3 for political spectrum coordinates."""

from __future__ import annotations

import math
from typing import Mapping


SCORING_MODEL_V3_SCALE_K = 0.015


def _score(scores: Mapping[str, float], key: str) -> float:
    try:
        return float(scores.get(key, 0.0))
    except Exception:
        return 0.0


def scale_axis_v3(raw: float, k: float = SCORING_MODEL_V3_SCALE_K) -> float:
    """Normalize a raw axis value into the graph range [-4, 4]."""
    return 4.0 * math.tanh(k * raw)


def compute_scoring_model_v3_blocks(scores: Mapping[str, float]) -> dict[str, float]:
    """Return weighted scoring blocks and raw axes for the v3 coordinate model."""
    communisme = _score(scores, "communisme")
    capitalisme = _score(scores, "capitalisme")
    regulation = _score(scores, "regulation")
    laissez_faire = _score(scores, "laissez_faire")
    ecologie = _score(scores, "ecologie")
    productivisme = _score(scores, "productivisme")
    constructivisme = _score(scores, "constructivisme")
    essentialisme = _score(scores, "essentialisme")
    justice_rehabilitative = _score(scores, "justice_rehabilitative")
    justice_punitive = _score(scores, "justice_punitive")
    progressisme = _score(scores, "progressisme")
    conservatisme = _score(scores, "conservatisme")
    internationalisme = _score(scores, "internationalisme")
    nationalisme = _score(scores, "nationalisme")

    economic_left = (
        0.95 * communisme
        + 0.75 * regulation
        + 0.28 * ecologie
    )
    economic_right = (
        0.95 * capitalisme
        + 0.80 * laissez_faire
        + 0.24 * productivisme
    )

    social_libertarian = (
        0.75 * constructivisme
        + 0.70 * justice_rehabilitative
        + 0.75 * progressisme
        + 0.35 * internationalisme
    )
    social_authoritarian = (
        0.60 * essentialisme
        + 0.70 * justice_punitive
        + 0.70 * conservatisme
        + 0.30 * nationalisme
    )

    economic_raw = economic_right - economic_left
    social_raw = social_authoritarian - social_libertarian

    economic_raw += 0.04 * (productivisme - ecologie)
    social_raw += 0.03 * (nationalisme - internationalisme)

    return {
        "economic_left": economic_left,
        "economic_right": economic_right,
        "social_libertarian": social_libertarian,
        "social_authoritarian": social_authoritarian,
        "economic_raw": economic_raw,
        "social_raw": social_raw,
    }


def compute_scoring_model_v3_coordinates(scores: Mapping[str, float]) -> tuple[float, float]:
    """Return x/y coordinates using the canonical v3 formula."""
    blocks = compute_scoring_model_v3_blocks(scores)
    return (
        scale_axis_v3(blocks["economic_raw"]),
        scale_axis_v3(blocks["social_raw"]),
    )
