from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from political_spectrum_analyzer.model.scoring_model_v2 import (
    compute_projection_breakdown,
    compute_secondary_dimensions,
)


@dataclass(frozen=True)
class AxisInsight:
    axis: str
    score: float
    interpretation: str


@dataclass(frozen=True)
class AdvancedProfileInterpretation:
    profile_name: str
    short_summary: str
    detailed_summary: str
    economic_reading: str
    societal_reading: str
    method_reading: str
    coherence_score: float
    intensity_score: float
    moderation_score: float
    radicality_score: float
    dominant_axes: tuple[AxisInsight, ...]
    weak_axes: tuple[AxisInsight, ...]
    secondary_dimensions: dict[str, float]


AXIS_LABELS: dict[str, str] = {
    "constructivisme": "constructivist social reading",
    "essentialisme": "essentialist social reading",
    "justice_rehabilitative": "rehabilitative justice",
    "justice_punitive": "punitive justice",
    "progressisme": "progressive social change",
    "conservatisme": "conservative continuity",
    "internationalisme": "international openness",
    "nationalisme": "national sovereignty",
    "communisme": "collective economic ownership",
    "capitalisme": "market and private ownership",
    "regulation": "public economic regulation",
    "laissez_faire": "market autonomy",
    "ecologie": "ecological constraint",
    "productivisme": "productive growth",
    "revolution": "rupture-oriented change",
    "reformisme": "institutional reform",
}


def _as_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _clean_scores(scores: Mapping[str, object]) -> dict[str, float]:
    return {axis: _as_float(value) for axis, value in scores.items()}


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def compute_intensity_score(scores: Mapping[str, object]) -> float:
    deviations = [abs(value - 50.0) for value in _clean_scores(scores).values()]
    return round(min(100.0, _mean(deviations) * 2.0), 2)


def compute_moderation_score(scores: Mapping[str, object]) -> float:
    return round(100.0 - compute_intensity_score(scores), 2)


def compute_radicality_score(scores: Mapping[str, object]) -> float:
    revolution = _as_float(scores.get("revolution"))
    reformism = _as_float(scores.get("reformisme"))
    return round(min(100.0, max(0.0, revolution - reformism)), 2)


def compute_coherence_score(scores: Mapping[str, object]) -> float:
    pairs = [
        ("constructivisme", "essentialisme"),
        ("justice_rehabilitative", "justice_punitive"),
        ("progressisme", "conservatisme"),
        ("internationalisme", "nationalisme"),
        ("communisme", "capitalisme"),
        ("regulation", "laissez_faire"),
        ("ecologie", "productivisme"),
        ("revolution", "reformisme"),
    ]

    penalties = []
    for left, right in pairs:
        simultaneous_high = max(0.0, min(_as_float(scores.get(left)), _as_float(scores.get(right))) - 50.0)
        penalties.append(simultaneous_high)

    return round(max(0.0, min(100.0, 100.0 - _mean(penalties) * 2.0)), 2)


def _axis_insights(scores: Mapping[str, object], reverse: bool, limit: int = 5) -> tuple[AxisInsight, ...]:
    sorted_scores = sorted(_clean_scores(scores).items(), key=lambda item: item[1], reverse=reverse)[:limit]
    insights = []

    for axis, score in sorted_scores:
        label = AXIS_LABELS.get(axis, axis.replace("_", " "))
        prefix = "Strong marker of" if reverse else "Weak marker of"
        insights.append(AxisInsight(axis=axis, score=round(score, 2), interpretation=f"{prefix} {label}."))

    return tuple(insights)


def _economic_reading(x: float, dimensions: Mapping[str, float]) -> str:
    eco_balance = dimensions.get("eco_productivism_balance", 0.0)

    if x <= -2.5:
        base = "The profile is clearly positioned on the economic left."
    elif x < -0.75:
        base = "The profile leans toward the economic left."
    elif x < 0.75:
        base = "The profile is economically mixed or close to the center."
    elif x < 2.5:
        base = "The profile leans toward the economic right."
    else:
        base = "The profile is clearly positioned on the economic right."

    if eco_balance <= -35:
        return base + " It prioritizes ecological constraint over productivist expansion."
    if eco_balance >= 35:
        return base + " It prioritizes production, growth, and infrastructure over ecological constraint."
    return base + " Its ecology/productivism balance is not extremely polarized."


def _societal_reading(y: float, dimensions: Mapping[str, float]) -> str:
    globalism = dimensions.get("globalism_balance", 0.0)
    justice = dimensions.get("justice_balance", 0.0)

    if y <= -2.5:
        base = "The profile is strongly libertarian or progressive on the societal axis."
    elif y < -0.75:
        base = "The profile leans libertarian or progressive on the societal axis."
    elif y < 0.75:
        base = "The profile is societally mixed or close to the center."
    elif y < 2.5:
        base = "The profile leans authoritarian or conservative on the societal axis."
    else:
        base = "The profile is strongly authoritarian or conservative on the societal axis."

    if globalism >= 35:
        base += " It is marked by strong international openness."
    elif globalism <= -35:
        base += " It is marked by strong national-sovereignty orientation."

    if justice >= 35:
        base += " Its justice preferences are more rehabilitative than punitive."
    elif justice <= -35:
        base += " Its justice preferences are more punitive than rehabilitative."

    return base


def _method_reading(dimensions: Mapping[str, float]) -> str:
    method = dimensions.get("change_method", 0.0)

    if method >= 45:
        return "The profile favors rupture-oriented political change rather than gradual institutional reform."
    if method >= 15:
        return "The profile shows a moderate preference for rupture or systemic transformation."
    if method <= -45:
        return "The profile strongly favors institutional reform and gradual change over rupture."
    if method <= -15:
        return "The profile shows a moderate preference for reformist and institutional change."
    return "The profile is balanced between rupture-oriented change and reformist change."


def _short_summary(x: float, y: float, intensity: float, coherence: float) -> str:
    economic = "economically left-leaning" if x < -0.75 else "economically right-leaning" if x > 0.75 else "economically mixed"
    societal = "societally libertarian/progressive" if y < -0.75 else "societally authoritarian/conservative" if y > 0.75 else "societally mixed"
    intensity_text = "highly marked" if intensity >= 70 else "moderately marked" if intensity >= 40 else "relatively moderate"
    coherence_text = "internally coherent" if coherence >= 80 else "somewhat coherent" if coherence >= 60 else "internally tense"
    return f"This is a {intensity_text}, {coherence_text} profile: {economic} and {societal}."


def build_advanced_profile_interpretation(
    profile_name: str,
    scores: Mapping[str, object],
    x: float | None = None,
    y: float | None = None,
) -> AdvancedProfileInterpretation:
    breakdown = compute_projection_breakdown(scores)
    final_x = breakdown.x if x is None else float(x)
    final_y = breakdown.y if y is None else float(y)
    dimensions = compute_secondary_dimensions(scores)

    intensity = compute_intensity_score(scores)
    moderation = compute_moderation_score(scores)
    radicality = compute_radicality_score(scores)
    coherence = compute_coherence_score(scores)

    economic_reading = _economic_reading(final_x, dimensions)
    societal_reading = _societal_reading(final_y, dimensions)
    method_reading = _method_reading(dimensions)
    short_summary = _short_summary(final_x, final_y, intensity, coherence)
    detailed_summary = (
        f"{economic_reading} {societal_reading} {method_reading} "
        f"The intensity score is {intensity:.1f}/100, the moderation score is {moderation:.1f}/100, "
        f"the radicality score is {radicality:.1f}/100, and the coherence score is {coherence:.1f}/100."
    )

    return AdvancedProfileInterpretation(
        profile_name=profile_name,
        short_summary=short_summary,
        detailed_summary=detailed_summary,
        economic_reading=economic_reading,
        societal_reading=societal_reading,
        method_reading=method_reading,
        coherence_score=coherence,
        intensity_score=intensity,
        moderation_score=moderation,
        radicality_score=radicality,
        dominant_axes=_axis_insights(scores, reverse=True),
        weak_axes=_axis_insights(scores, reverse=False),
        secondary_dimensions={key: round(value, 4) for key, value in dimensions.items()},
    )


def build_advanced_interpretation_rows(interpretations: list[AdvancedProfileInterpretation]) -> list[dict[str, object]]:
    return [
        {
            "profile_name": item.profile_name,
            "coherence_score": item.coherence_score,
            "intensity_score": item.intensity_score,
            "moderation_score": item.moderation_score,
            "radicality_score": item.radicality_score,
            "summary": item.short_summary,
            "change_method": item.secondary_dimensions.get("change_method", 0.0),
            "eco_productivism_balance": item.secondary_dimensions.get("eco_productivism_balance", 0.0),
            "globalism_balance": item.secondary_dimensions.get("globalism_balance", 0.0),
            "justice_balance": item.secondary_dimensions.get("justice_balance", 0.0),
            "social_change_balance": item.secondary_dimensions.get("social_change_balance", 0.0),
        }
        for item in interpretations
    ]
