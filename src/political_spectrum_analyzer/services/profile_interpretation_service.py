from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class AxisInterpretation:
    axis: str
    label: str
    score: int
    level: str
    interpretation: str


@dataclass(frozen=True)
class ProfileInterpretation:
    profile_name: str
    dominant_axes: list[AxisInterpretation]
    weak_axes: list[AxisInterpretation]
    axis_pair_balances: list[dict[str, object]]
    synthesis: str
    economic_reading: str
    societal_reading: str
    strategic_reading: str


AXIS_LABELS: dict[str, str] = {
    "constructivisme": "Constructivism",
    "essentialisme": "Essentialism",
    "justice_rehabilitative": "Rehabilitative justice",
    "justice_punitive": "Punitive justice",
    "progressisme": "Progressivism",
    "conservatisme": "Conservatism",
    "internationalisme": "Internationalism",
    "nationalisme": "Nationalism",
    "communisme": "Communism",
    "capitalisme": "Capitalism",
    "regulation": "Regulation",
    "laissez_faire": "Laissez-faire",
    "ecologie": "Ecology",
    "productivisme": "Productivism",
    "revolution": "Revolution",
    "reformisme": "Reformism",
}


AXIS_INTERPRETATIONS: dict[str, str] = {
    "constructivisme": "Interprets social norms, identities, and institutions as shaped by context, history, and collective construction.",
    "essentialisme": "Values stable categories, inherited structures, and more fixed interpretations of identity or society.",
    "justice_rehabilitative": "Leans toward prevention, reintegration, and rehabilitation rather than pure punishment.",
    "justice_punitive": "Emphasizes order, deterrence, responsibility, and firmer sanctions.",
    "progressisme": "Supports social reform, modernization of norms, and expansion of rights.",
    "conservatisme": "Values continuity, tradition, institutional stability, and caution toward rapid social change.",
    "internationalisme": "Shows openness toward cross-border cooperation, global solidarity, and international coordination.",
    "nationalisme": "Prioritizes sovereignty, national cohesion, identity, and domestic collective interest.",
    "communisme": "Includes strong redistribution, collective ownership logic, or anti-capitalist tendencies.",
    "capitalisme": "Gives importance to markets, private ownership, entrepreneurship, and capital accumulation.",
    "regulation": "Supports public oversight, institutional correction of markets, and rules limiting economic excesses.",
    "laissez_faire": "Favors market autonomy, deregulation, and limited state intervention in economic activity.",
    "ecologie": "Gives importance to environmental constraints, sustainability, and ecological responsibility.",
    "productivisme": "Values production, growth, industrial capacity, infrastructure, and material expansion.",
    "revolution": "Is open to rupture, systemic transformation, or deep institutional change.",
    "reformisme": "Prefers gradual change, legal continuity, negotiation, and institutional reform.",
}


AXIS_PAIRS: list[tuple[str, str, str]] = [
    ("constructivisme", "essentialisme", "Social philosophy"),
    ("justice_rehabilitative", "justice_punitive", "Justice orientation"),
    ("progressisme", "conservatisme", "Social change"),
    ("internationalisme", "nationalisme", "Political community"),
    ("communisme", "capitalisme", "Ownership model"),
    ("regulation", "laissez_faire", "Market governance"),
    ("ecologie", "productivisme", "Ecology vs production"),
    ("revolution", "reformisme", "Political strategy"),
]


def _score_level(score: int) -> str:
    if score >= 75:
        return "Very high"
    if score >= 60:
        return "High"
    if score >= 40:
        return "Moderate"
    if score >= 25:
        return "Low"
    return "Very low"


def _safe_score(scores: Mapping[str, int], axis: str) -> int:
    value = int(scores.get(axis, 0))
    return max(0, min(100, value))


def _axis_interpretation(axis: str, score: int) -> AxisInterpretation:
    return AxisInterpretation(
        axis=axis,
        label=AXIS_LABELS.get(axis, axis.replace("_", " ").title()),
        score=score,
        level=_score_level(score),
        interpretation=AXIS_INTERPRETATIONS.get(axis, ""),
    )


def get_dominant_axes(scores: Mapping[str, int], limit: int = 5) -> list[AxisInterpretation]:
    axes = [_axis_interpretation(axis, _safe_score(scores, axis)) for axis in AXIS_LABELS]
    axes.sort(key=lambda item: item.score, reverse=True)
    return axes[:limit]


def get_weak_axes(scores: Mapping[str, int], limit: int = 5) -> list[AxisInterpretation]:
    axes = [_axis_interpretation(axis, _safe_score(scores, axis)) for axis in AXIS_LABELS]
    axes.sort(key=lambda item: item.score)
    return axes[:limit]


def get_axis_pair_balances(scores: Mapping[str, int]) -> list[dict[str, object]]:
    balances: list[dict[str, object]] = []

    for left_axis, right_axis, label in AXIS_PAIRS:
        left_score = _safe_score(scores, left_axis)
        right_score = _safe_score(scores, right_axis)
        delta = left_score - right_score

        if abs(delta) <= 10:
            leading_side = "Balanced"
            reading = f"{label}: balanced between {AXIS_LABELS[left_axis]} and {AXIS_LABELS[right_axis]}."
        elif delta > 0:
            leading_side = AXIS_LABELS[left_axis]
            reading = f"{label}: stronger {AXIS_LABELS[left_axis]} tendency."
        else:
            leading_side = AXIS_LABELS[right_axis]
            reading = f"{label}: stronger {AXIS_LABELS[right_axis]} tendency."

        balances.append(
            {
                "dimension": label,
                "left_axis": AXIS_LABELS[left_axis],
                "left_score": left_score,
                "right_axis": AXIS_LABELS[right_axis],
                "right_score": right_score,
                "delta": delta,
                "leading_side": leading_side,
                "reading": reading,
            }
        )

    return balances


def _average(scores: Mapping[str, int], axes: list[str]) -> float:
    return sum(_safe_score(scores, axis) for axis in axes) / len(axes)


def build_economic_reading(scores: Mapping[str, int]) -> str:
    left_avg = _average(scores, ["communisme", "regulation", "ecologie"])
    right_avg = _average(scores, ["capitalisme", "laissez_faire", "productivisme"])

    if abs(left_avg - right_avg) <= 8:
        return "Economically, the profile is relatively balanced: interventionist and market-oriented signals coexist."
    if left_avg > right_avg:
        return "Economically, the profile leans toward intervention, redistribution, ecological constraint, or collective economic logic."
    return "Economically, the profile leans toward market autonomy, private initiative, production, or lower intervention."


def build_societal_reading(scores: Mapping[str, int]) -> str:
    progressive_avg = _average(scores, ["constructivisme", "justice_rehabilitative", "progressisme", "internationalisme"])
    conservative_avg = _average(scores, ["essentialisme", "justice_punitive", "conservatisme", "nationalisme"])

    if abs(progressive_avg - conservative_avg) <= 8:
        return "Societally, the profile is mixed or moderate: progressive and order-oriented signals coexist."
    if progressive_avg > conservative_avg:
        return "Societally, the profile leans progressive, open to social change, rehabilitation, and broader cooperation."
    return "Societally, the profile leans conservative or order-oriented, with stronger emphasis on stability, authority, or national cohesion."


def build_strategic_reading(scores: Mapping[str, int]) -> str:
    revolution = _safe_score(scores, "revolution")
    reformism = _safe_score(scores, "reformisme")

    if abs(revolution - reformism) <= 10:
        return "Strategically, the profile balances systemic-change instincts with institutional or gradualist reform."
    if revolution > reformism:
        return "Strategically, the profile is more rupture-oriented and receptive to deeper systemic transformation."
    return "Strategically, the profile is more reformist, favoring gradual change through existing institutions."


def build_profile_synthesis(profile_name: str, scores: Mapping[str, int]) -> str:
    dominant_axes = get_dominant_axes(scores, limit=3)
    strongest_labels = ", ".join(axis.label for axis in dominant_axes)

    return (
        f"{profile_name} is mainly characterized by strong scores in {strongest_labels}. "
        f"{build_economic_reading(scores)} "
        f"{build_societal_reading(scores)} "
        f"{build_strategic_reading(scores)}"
    )


def interpret_profile(profile_name: str, scores: Mapping[str, int]) -> ProfileInterpretation:
    return ProfileInterpretation(
        profile_name=profile_name,
        dominant_axes=get_dominant_axes(scores),
        weak_axes=get_weak_axes(scores),
        axis_pair_balances=get_axis_pair_balances(scores),
        synthesis=build_profile_synthesis(profile_name, scores),
        economic_reading=build_economic_reading(scores),
        societal_reading=build_societal_reading(scores),
        strategic_reading=build_strategic_reading(scores),
    )