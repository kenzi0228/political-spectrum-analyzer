from __future__ import annotations

from dataclasses import dataclass
from math import tanh
from typing import Mapping

GRAPH_LIMIT = 4.0
MODEL_SCALE_K = 0.016

ECONOMIC_LEFT_WEIGHTS = {"communisme": 0.95, "regulation": 0.75, "ecologie": 0.38}
ECONOMIC_RIGHT_WEIGHTS = {"capitalisme": 0.95, "laissez_faire": 0.80, "productivisme": 0.32}
SOCIAL_LIBERTARIAN_WEIGHTS = {
    "constructivisme": 0.75,
    "justice_rehabilitative": 0.70,
    "progressisme": 0.75,
    "internationalisme": 0.45,
}
SOCIAL_AUTHORITARIAN_WEIGHTS = {
    "essentialisme": 0.65,
    "justice_punitive": 0.75,
    "conservatisme": 0.75,
    "nationalisme": 0.45,
}


@dataclass(frozen=True)
class ProjectionBreakdown:
    economic_left: float
    economic_right: float
    social_libertarian: float
    social_authoritarian: float
    economic_adjustment: float
    social_adjustment: float
    x_raw: float
    y_raw: float
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


def scale_raw_score(raw: float, k: float = MODEL_SCALE_K, graph_limit: float = GRAPH_LIMIT) -> float:
    return tanh(k * raw) * graph_limit


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

    economic_adjustment = 0.10 * (_score(scores, "productivisme") - _score(scores, "ecologie"))
    social_adjustment = 0.06 * (_score(scores, "nationalisme") - _score(scores, "internationalisme"))

    x_raw = economic_right - economic_left + economic_adjustment
    y_raw = social_authoritarian - social_libertarian + social_adjustment

    x = scale_raw_score(x_raw)
    y = scale_raw_score(y_raw)

    return ProjectionBreakdown(
        economic_left=round(economic_left, 4),
        economic_right=round(economic_right, 4),
        social_libertarian=round(social_libertarian, 4),
        social_authoritarian=round(social_authoritarian, 4),
        economic_adjustment=round(economic_adjustment, 4),
        social_adjustment=round(social_adjustment, 4),
        x_raw=round(x_raw, 4),
        y_raw=round(y_raw, 4),
        x=round(x, 3),
        y=round(y, 3),
        secondary_dimensions={k: round(v, 4) for k, v in compute_secondary_dimensions(scores).items()},
    )


def compute_position(scores: Mapping[str, object]) -> tuple[float, float]:
    breakdown = compute_projection_breakdown(scores)
    return breakdown.x, breakdown.y
