from __future__ import annotations

from political_spectrum_analyzer.model.scoring_model_v2 import compute_secondary_dimensions

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
    archetype: str
    tension_reading: str
    profile_highlights: list[str]


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


def _average(scores: Mapping[str, int], axes: list[str]) -> float:
    return sum(_safe_score(scores, axis) for axis in axes) / len(axes)


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


def build_economic_reading(scores: Mapping[str, int]) -> str:
    left_avg = _average(scores, ["communisme", "regulation", "ecologie"])
    right_avg = _average(scores, ["capitalisme", "laissez_faire", "productivisme"])

    if abs(left_avg - right_avg) <= 8:
        return "Economically, the profile combines interventionist and market-oriented signals rather than following a single economic direction."
    if left_avg > right_avg:
        if _safe_score(scores, "ecologie") >= 65:
            return "Economically, the profile leans interventionist with a strong ecological and regulatory component."
        return "Economically, the profile leans toward redistribution, public intervention, and collective economic correction."
    if _safe_score(scores, "productivisme") >= 65:
        return "Economically, the profile leans market-oriented with a strong emphasis on production, growth, and capacity."
    return "Economically, the profile leans toward market autonomy, private initiative, and lower intervention."


def build_societal_reading(scores: Mapping[str, int]) -> str:
    progressive_avg = _average(scores, ["constructivisme", "justice_rehabilitative", "progressisme", "internationalisme"])
    conservative_avg = _average(scores, ["essentialisme", "justice_punitive", "conservatisme", "nationalisme"])

    if abs(progressive_avg - conservative_avg) <= 8:
        return "Societally, the profile combines progressive and order-oriented signals, producing a mixed social posture."
    if progressive_avg > conservative_avg:
        if _safe_score(scores, "internationalisme") >= 65:
            return "Societally, the profile leans progressive with a strong international and cooperative orientation."
        return "Societally, the profile leans progressive, reform-oriented, and open to social change."
    if _safe_score(scores, "nationalisme") >= 65:
        return "Societally, the profile leans order-oriented with a pronounced national-sovereignty component."
    return "Societally, the profile leans conservative or stability-oriented, with emphasis on continuity and order."


def build_strategic_reading(scores: Mapping[str, int]) -> str:
    revolution = _safe_score(scores, "revolution")
    reformism = _safe_score(scores, "reformisme")

    if abs(revolution - reformism) <= 10:
        return "Strategically, the profile balances systemic-change instincts with gradual institutional reform."
    if revolution > reformism:
        return "Strategically, the profile is more rupture-oriented and receptive to deep systemic transformation."
    return "Strategically, the profile is more reformist, favoring gradual change through existing institutions."


def build_profile_archetype(scores: Mapping[str, int]) -> str:
    left_avg = _average(scores, ["communisme", "regulation", "ecologie"])
    right_avg = _average(scores, ["capitalisme", "laissez_faire", "productivisme"])
    progressive_avg = _average(scores, ["constructivisme", "justice_rehabilitative", "progressisme", "internationalisme"])
    conservative_avg = _average(scores, ["essentialisme", "justice_punitive", "conservatisme", "nationalisme"])

    economic_side = "left" if left_avg > right_avg + 8 else "right" if right_avg > left_avg + 8 else "center"
    social_side = "progressive" if progressive_avg > conservative_avg + 8 else "conservative" if conservative_avg > progressive_avg + 8 else "mixed"

    if economic_side == "left" and social_side == "progressive":
        return "Progressive left profile"
    if economic_side == "left" and social_side == "conservative":
        return "Socially conservative left profile"
    if economic_side == "right" and social_side == "progressive":
        return "Liberal-market progressive profile"
    if economic_side == "right" and social_side == "conservative":
        return "Conservative market-oriented profile"
    if economic_side == "center" and social_side == "progressive":
        return "Social-progressive centrist profile"
    if economic_side == "center" and social_side == "conservative":
        return "Order-oriented centrist profile"
    return "Balanced or composite profile"


def build_tension_reading(scores: Mapping[str, int]) -> str:
    balances = get_axis_pair_balances(scores)
    strongest_tension = max(balances, key=lambda row: abs(int(row["delta"])))

    if abs(int(strongest_tension["delta"])) <= 10:
        return "The profile does not show a single dominant internal opposition; most axis pairs are relatively balanced."

    return (
        "The strongest internal contrast appears in "
        f"{strongest_tension['dimension']}: {strongest_tension['leading_side']} dominates this pair."
    )


def build_profile_highlights(scores: Mapping[str, int]) -> list[str]:
    highlights: list[str] = []

    dominant = get_dominant_axes(scores, limit=4)
    weak = get_weak_axes(scores, limit=2)

    if dominant:
        labels = ", ".join(axis.label for axis in dominant[:3])
        highlights.append(f"Core drivers: {labels}.")

    for axis in dominant[:4]:
        if axis.score >= 75:
            highlights.append(f"{axis.label} is a very strong marker of this profile ({axis.score}/100).")
        elif axis.score >= 60:
            highlights.append(f"{axis.label} clearly contributes to the profile direction ({axis.score}/100).")

    if weak:
        weak_labels = ", ".join(axis.label for axis in weak)
        highlights.append(f"Low-impact dimensions in this profile: {weak_labels}.")

    return highlights[:6]


def build_profile_synthesis(profile_name: str, scores: Mapping[str, int]) -> str:
    archetype = build_profile_archetype(scores)
    dominant_axes = get_dominant_axes(scores, limit=3)
    strongest_labels = ", ".join(axis.label for axis in dominant_axes)

    return (
        f"{profile_name} is best read as a {archetype.lower()}. "
        f"The strongest drivers are {strongest_labels}. "
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
        archetype=build_profile_archetype(scores),
        tension_reading=build_tension_reading(scores),
        profile_highlights=build_profile_highlights(scores),
    )

# Secondary dimensions from scoring model v2 are available for advanced interpretation.
# Revolution and reformism stay outside x/y placement and are used as qualitative dimensions.
