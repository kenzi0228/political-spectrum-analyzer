from __future__ import annotations

from political_spectrum_analyzer.model.scoring_model_v2 import compute_position as compute_position_v2, compute_projection_breakdown

from political_spectrum_analyzer.constants import (
    PLOT_X_MAX,
    PLOT_X_MIN,
    PLOT_Y_MAX,
    PLOT_Y_MIN,
)
from political_spectrum_analyzer.domain.models import PersonResult, PersonScores
from political_spectrum_analyzer.domain.validation import validate_scores


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def compute_person_result(person: PersonScores) -> PersonResult:
    validate_scores(person.scores)
    x_val, y_val = compute_position_v2(person.scores)

    return PersonResult(
        name=person.name,
        scores=person.scores,
        x=clamp(float(x_val), PLOT_X_MIN, PLOT_X_MAX),
        y=clamp(float(y_val), PLOT_Y_MIN, PLOT_Y_MAX),
    )

# ---------------------------------------------------------------------------
# Scoring model v2 service helpers
# ---------------------------------------------------------------------------

def compute_profile_position_v2(scores):
    return compute_position_v2(scores)


def compute_profile_projection_breakdown_v2(scores):
    return compute_projection_breakdown(scores)
