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
    intensity_score: float
    coherence_score: float
    center_of_gravity: str
    synthesis: str
    economic_reading: str
    societal_reading: str
    strategic_reading: str
    archetype: str
    tension_reading: str
    profile_highlights: list[str]
    diagnostic_notes: list[str]
    score_notes: list[AxisInterpretation]


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


def _score_sensitive_interpretation(axis: str, score: int) -> str:
    base = AXIS_INTERPRETATIONS.get(axis, "")

    if score >= 75:
        return f"Very strong marker. {base}"
    if score >= 60:
        return f"Clear marker. {base}"
    if score >= 40:
        return f"Moderate signal. {base}"
    if score >= 25:
        return f"Weak signal. {base}"
    return f"Very weak or marginal signal. {base}"


def _axis_interpretation(axis: str, score: int) -> AxisInterpretation:
    return AxisInterpretation(
        axis=axis,
        label=AXIS_LABELS.get(axis, axis.replace("_", " ").title()),
        score=score,
        level=_score_level(score),
        interpretation=_score_sensitive_interpretation(axis, score),
    )


def get_dominant_axes(scores: Mapping[str, int], limit: int = 5) -> list[AxisInterpretation]:
    axes = [_axis_interpretation(axis, _safe_score(scores, axis)) for axis in AXIS_LABELS]
    axes.sort(key=lambda item: item.score, reverse=True)
    return axes[:limit]


def get_weak_axes(scores: Mapping[str, int], limit: int = 5) -> list[AxisInterpretation]:
    axes = [_axis_interpretation(axis, _safe_score(scores, axis)) for axis in AXIS_LABELS]
    axes.sort(key=lambda item: item.score)
    return axes[:limit]


def get_score_notes(scores: Mapping[str, int]) -> list[AxisInterpretation]:
    return [_axis_interpretation(axis, _safe_score(scores, axis)) for axis in AXIS_LABELS]


def compute_intensity_score(scores: Mapping[str, int]) -> float:
    """Return how strongly the profile departs from a neutral 50/100 baseline."""
    distances = [abs(_safe_score(scores, axis) - 50) for axis in AXIS_LABELS]
    return round((sum(distances) / len(distances)) * 2, 1)


def compute_coherence_score(scores: Mapping[str, int]) -> float:
    """Estimate internal coherence by penalizing simultaneously high opposite poles."""
    penalty = 0.0

    for left_axis, right_axis, _label in AXIS_PAIRS:
        left_score = _safe_score(scores, left_axis)
        right_score = _safe_score(scores, right_axis)
        if left_score >= 60 and right_score >= 60:
            penalty += min(left_score, right_score) - 50

    cross_axis_pairs = [
        ("capitalisme", "regulation"),
        ("progressisme", "justice_punitive"),
        ("ecologie", "productivisme"),
        ("internationalisme", "nationalisme"),
    ]
    for left_axis, right_axis in cross_axis_pairs:
        left_score = _safe_score(scores, left_axis)
        right_score = _safe_score(scores, right_axis)
        if left_score >= 65 and right_score >= 65:
            penalty += (min(left_score, right_score) - 55) * 0.75

    return round(max(0.0, min(100.0, 100.0 - penalty)), 1)


def get_axis_pair_balances(scores: Mapping[str, int]) -> list[dict[str, object]]:
    balances: list[dict[str, object]] = []

    for left_axis, right_axis, label in AXIS_PAIRS:
        left_score = _safe_score(scores, left_axis)
        right_score = _safe_score(scores, right_axis)
        delta = left_score - right_score

        if left_score >= 60 and right_score >= 60:
            leading_side = "Internally mixed"
            reading = (
                f"{label}: both {AXIS_LABELS[left_axis]} and {AXIS_LABELS[right_axis]} are high, "
                "so this pair should be read as a real internal tension rather than a simple winner."
            )
        elif left_score <= 35 and right_score <= 35:
            leading_side = "Muted"
            reading = (
                f"{label}: both poles are weak, so this dimension does not strongly structure the profile."
            )
        elif abs(delta) <= 10:
            leading_side = "Balanced"
            reading = f"{label}: balanced between {AXIS_LABELS[left_axis]} and {AXIS_LABELS[right_axis]}."
        elif delta > 0:
            leading_side = AXIS_LABELS[left_axis]
            reading = f"{label}: stronger {AXIS_LABELS[left_axis]} tendency by {abs(delta)} points."
        else:
            leading_side = AXIS_LABELS[right_axis]
            reading = f"{label}: stronger {AXIS_LABELS[right_axis]} tendency by {abs(delta)} points."

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


def build_center_of_gravity(scores: Mapping[str, int]) -> str:
    left_avg = _average(scores, ["communisme", "regulation", "ecologie"])
    right_avg = _average(scores, ["capitalisme", "laissez_faire", "productivisme"])
    progressive_avg = _average(scores, ["constructivisme", "justice_rehabilitative", "progressisme", "internationalisme"])
    conservative_avg = _average(scores, ["essentialisme", "justice_punitive", "conservatisme", "nationalisme"])
    revolution = _safe_score(scores, "revolution")
    reformism = _safe_score(scores, "reformisme")

    if left_avg > right_avg + 8:
        economic = "economic-left"
    elif right_avg > left_avg + 8:
        economic = "economic-right"
    else:
        economic = "economically mixed"

    if progressive_avg > conservative_avg + 8:
        social = "progressive/libertarian"
    elif conservative_avg > progressive_avg + 8:
        social = "order-oriented/conservative"
    else:
        social = "socially mixed"

    if revolution > reformism + 10:
        strategy = "rupture-oriented"
    elif reformism > revolution + 10:
        strategy = "reformist"
    else:
        strategy = "strategically balanced"

    return f"{economic}, {social}, {strategy}"


def build_diagnostic_notes(scores: Mapping[str, int]) -> list[str]:
    notes: list[str] = []
    intensity = compute_intensity_score(scores)
    coherence = compute_coherence_score(scores)
    secondary = compute_secondary_dimensions(scores)

    if intensity >= 55:
        notes.append(f"High profile intensity ({intensity}/100): several scores are far from the neutral midpoint.")
    elif intensity <= 25:
        notes.append(f"Low profile intensity ({intensity}/100): most scores remain close to the center, so the graph position should be read cautiously.")
    else:
        notes.append(f"Moderate profile intensity ({intensity}/100): the profile has clear signals without being uniformly extreme.")

    if coherence >= 80:
        notes.append(f"High coherence ({coherence}/100): few opposing axes are simultaneously high.")
    elif coherence >= 55:
        notes.append(f"Mixed coherence ({coherence}/100): the profile contains some cross-pressures that deserve interpretation.")
    else:
        notes.append(f"Low coherence ({coherence}/100): several opposing axes are high at the same time, so tensions are central to the reading.")

    change_method = secondary["change_method"]
    if abs(change_method) >= 25:
        direction = "revolutionary rupture" if change_method > 0 else "institutional reform"
        notes.append(f"Strategic tilt: {direction} leads by {abs(round(change_method, 1))} points on the revolution/reformism balance.")

    globalism_balance = secondary["globalism_balance"]
    if abs(globalism_balance) >= 25:
        direction = "international cooperation" if globalism_balance > 0 else "national sovereignty"
        notes.append(f"Political-community tilt: {direction} clearly structures the profile.")

    return notes


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
    internal_tensions = build_internal_tensions(scores)
    if internal_tensions:
        return "Main internal tensions: " + " ".join(internal_tensions[:3])

    balances = get_axis_pair_balances(scores)
    strongest_tension = max(balances, key=lambda row: abs(int(row["delta"])))

    if abs(int(strongest_tension["delta"])) <= 10:
        return "The profile does not show a single dominant internal opposition; most axis pairs are relatively balanced."

    return (
        "The strongest internal contrast appears in "
        f"{strongest_tension['dimension']}: {strongest_tension['leading_side']} dominates this pair."
    )


def build_internal_tensions(scores: Mapping[str, int]) -> list[str]:
    tensions: list[str] = []

    pair_balances = get_axis_pair_balances(scores)
    for row in pair_balances:
        if row["leading_side"] == "Internally mixed":
            tensions.append(
                f"{row['dimension']} combines high {row['left_axis']} ({row['left_score']}/100) "
                f"with high {row['right_axis']} ({row['right_score']}/100)."
            )

    if _safe_score(scores, "capitalisme") >= 60 and _safe_score(scores, "regulation") >= 60:
        tensions.append(
            "The profile combines market/private-ownership support with a strong appetite for public regulation."
        )
    if _safe_score(scores, "progressisme") >= 60 and _safe_score(scores, "justice_punitive") >= 60:
        tensions.append(
            "The profile combines social-progressive instincts with a punitive conception of justice."
        )
    if _safe_score(scores, "ecologie") >= 60 and _safe_score(scores, "productivisme") >= 60:
        tensions.append(
            "The profile values both ecological limits and productive expansion, which can create policy trade-offs."
        )
    if _safe_score(scores, "internationalisme") >= 60 and _safe_score(scores, "nationalisme") >= 60:
        tensions.append(
            "The profile combines international openness with national-sovereignty priorities."
        )

    unique_tensions: list[str] = []
    seen = set()
    for tension in tensions:
        key = tension.lower()
        if key not in seen:
            unique_tensions.append(tension)
            seen.add(key)

    return unique_tensions


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

    sharpest_balance = max(get_axis_pair_balances(scores), key=lambda row: abs(int(row["delta"])))
    if abs(int(sharpest_balance["delta"])) > 20:
        highlights.append(
            f"Sharpest contrast: {sharpest_balance['dimension']} leans toward {sharpest_balance['leading_side']}."
        )

    internal_tensions = build_internal_tensions(scores)
    if internal_tensions:
        highlights.append(internal_tensions[0])

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
        f"{build_strategic_reading(scores)} "
        f"{build_tension_reading(scores)} "
        f"The center of gravity is {build_center_of_gravity(scores)}."
    )


def interpret_profile(profile_name: str, scores: Mapping[str, int]) -> ProfileInterpretation:
    return ProfileInterpretation(
        profile_name=profile_name,
        dominant_axes=get_dominant_axes(scores),
        weak_axes=get_weak_axes(scores),
        axis_pair_balances=get_axis_pair_balances(scores),
        intensity_score=compute_intensity_score(scores),
        coherence_score=compute_coherence_score(scores),
        center_of_gravity=build_center_of_gravity(scores),
        synthesis=build_profile_synthesis(profile_name, scores),
        economic_reading=build_economic_reading(scores),
        societal_reading=build_societal_reading(scores),
        strategic_reading=build_strategic_reading(scores),
        archetype=build_profile_archetype(scores),
        tension_reading=build_tension_reading(scores),
        profile_highlights=build_profile_highlights(scores),
        diagnostic_notes=build_diagnostic_notes(scores),
        score_notes=get_score_notes(scores),
    )

# Secondary dimensions from scoring model v2 are available for advanced interpretation.
# Revolution and reformism are direct but secondary v2 coordinate inputs and remain important qualitative dimensions.
