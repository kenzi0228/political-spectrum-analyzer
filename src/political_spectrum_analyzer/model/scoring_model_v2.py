from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Mapping

GRAPH_LIMIT = 4.0
NORMALIZATION_DENOMINATOR = 120.0
SIGMOID_STEEPNESS = 2.0

ECONOMIC_LEFT_WEIGHTS = {
    "communisme": 0.90,
    "regulation": 0.70,
    "ecologie": 0.35,
    "revolution": 0.25,
}
ECONOMIC_RIGHT_WEIGHTS = {
    "capitalisme": 0.90,
    "laissez_faire": 0.75,
    "productivisme": 0.25,
    "reformisme": 0.20,
}
SOCIAL_LIBERTARIAN_WEIGHTS = {
    "constructivisme": 0.70,
    "justice_rehabilitative": 0.65,
    "progressisme": 0.70,
    "internationalisme": 0.50,
}
SOCIAL_AUTHORITARIAN_WEIGHTS = {
    "essentialisme": 0.60,
    "justice_punitive": 0.70,
    "conservatisme": 0.70,
    "nationalisme": 0.50,
}


@dataclass(frozen=True)
class ProjectionBreakdown:
    economic_left: float
    economic_right: float
    social_libertarian: float
    social_authoritarian: float
    economic_adjustment: float
    social_adjustment: float
    strategic_adjustment: float
    x_raw: float
    y_raw: float
    economic_normalized: float
    social_normalized: float
    x: float
    y: float
    secondary_dimensions: dict[str, float]


def _score(scores: Mapping[str, object], axis: str) -> float:
    try:
        return float(scores.get(axis, 0.0))
    except (TypeError, ValueError):
        return 0.0


def _weighted_sum(scores: Mapping[str, object], weights: Mapping[str, float]) -> float:
    return sum(_score(scores, axis) * weight for axis, weight in weights.items())


def sigmoid_scaled(value: float, steepness: float = SIGMOID_STEEPNESS) -> float:
    """Map a normalized value to [-1, 1] using the legacy v2 sigmoid scale."""
    return (2.0 / (1.0 + exp(-steepness * value))) - 1.0


def scale_raw_score(
    raw: float,
    denominator: float = NORMALIZATION_DENOMINATOR,
    graph_limit: float = GRAPH_LIMIT,
) -> float:
    normalized = raw / denominator
    return graph_limit * sigmoid_scaled(normalized)


def compute_secondary_dimensions(scores: Mapping[str, object]) -> dict[str, float]:
    return {
        "change_method": _score(scores, "revolution") - _score(scores, "reformisme"),
        "eco_productivism_balance": _score(scores, "productivisme") - _score(scores, "ecologie"),
        "globalism_balance": _score(scores, "internationalisme") - _score(scores, "nationalisme"),
        "justice_balance": _score(scores, "justice_rehabilitative") - _score(scores, "justice_punitive"),
        "social_change_balance": _score(scores, "progressisme") - _score(scores, "conservatisme"),
    }


def compute_projection_breakdown(scores: Mapping[str, object]) -> ProjectionBreakdown:
    economic_left = _weighted_sum(scores, ECONOMIC_LEFT_WEIGHTS)
    economic_right = _weighted_sum(scores, ECONOMIC_RIGHT_WEIGHTS)
    social_libertarian = _weighted_sum(scores, SOCIAL_LIBERTARIAN_WEIGHTS)
    social_authoritarian = _weighted_sum(scores, SOCIAL_AUTHORITARIAN_WEIGHTS)

    economic_adjustment = 0.12 * (_score(scores, "productivisme") - _score(scores, "ecologie"))
    social_adjustment = 0.10 * (_score(scores, "nationalisme") - _score(scores, "internationalisme"))
    strategic_adjustment = 0.08 * (_score(scores, "revolution") - _score(scores, "reformisme"))

    x_raw = economic_right - economic_left + economic_adjustment
    y_raw = social_authoritarian - social_libertarian + social_adjustment + strategic_adjustment

    economic_normalized = x_raw / NORMALIZATION_DENOMINATOR
    social_normalized = y_raw / NORMALIZATION_DENOMINATOR

    x = scale_raw_score(x_raw)
    y = scale_raw_score(y_raw)

    return ProjectionBreakdown(
        economic_left=round(economic_left, 4),
        economic_right=round(economic_right, 4),
        social_libertarian=round(social_libertarian, 4),
        social_authoritarian=round(social_authoritarian, 4),
        economic_adjustment=round(economic_adjustment, 4),
        social_adjustment=round(social_adjustment, 4),
        strategic_adjustment=round(strategic_adjustment, 4),
        x_raw=round(x_raw, 4),
        y_raw=round(y_raw, 4),
        economic_normalized=round(economic_normalized, 4),
        social_normalized=round(social_normalized, 4),
        x=round(x, 3),
        y=round(y, 3),
        secondary_dimensions={k: round(v, 4) for k, v in compute_secondary_dimensions(scores).items()},
    )


def compute_position(scores: Mapping[str, object]) -> tuple[float, float]:
    breakdown = compute_projection_breakdown(scores)
    return breakdown.x, breakdown.y
