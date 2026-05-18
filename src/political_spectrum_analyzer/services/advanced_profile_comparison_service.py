from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import sqrt
from typing import Iterable, Mapping

from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.model.scoring_model_v2 import compute_secondary_dimensions


@dataclass(frozen=True)
class DimensionDifference:
    dimension: str
    first_value: float
    second_value: float
    absolute_gap: float


@dataclass(frozen=True)
class AxisGap:
    axis: str
    first_score: float
    second_score: float
    absolute_gap: float


@dataclass(frozen=True)
class AdvancedProfileComparison:
    first_name: str
    second_name: str
    coordinate_distance: float
    global_similarity_score: float
    economic_similarity_score: float
    societal_similarity_score: float
    secondary_similarity_score: float
    closest_dimension: str
    most_divergent_dimension: str
    shared_dominant_axes: tuple[str, ...]
    shared_weak_axes: tuple[str, ...]
    largest_axis_gaps: tuple[AxisGap, ...]
    secondary_dimension_gaps: tuple[DimensionDifference, ...]
    summary: str
    detailed_summary: str


def _as_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _scores(person: PersonResult) -> Mapping[str, object]:
    return person.scores or {}


def _axis_value(person: PersonResult, axis: str) -> float:
    return _as_float(_scores(person).get(axis, 0.0))


def _distance_to_similarity(distance: float, max_distance: float) -> float:
    if max_distance <= 0:
        raise ValueError("max_distance must be positive")

    score = 100.0 * (1.0 - min(distance, max_distance) / max_distance)
    return round(max(0.0, min(100.0, score)), 2)


def compute_coordinate_distance(first: PersonResult, second: PersonResult) -> float:
    return sqrt((first.x - second.x) ** 2 + (first.y - second.y) ** 2)


def compute_global_similarity(first: PersonResult, second: PersonResult) -> float:
    return _distance_to_similarity(compute_coordinate_distance(first, second), max_distance=8.0)


def _axis_group_distance(first: PersonResult, second: PersonResult, axes: tuple[str, ...]) -> float:
    if not axes:
        return 0.0

    squared = sum((_axis_value(first, axis) - _axis_value(second, axis)) ** 2 for axis in axes)

    return sqrt(squared / len(axes))


def _axis_group_similarity(first: PersonResult, second: PersonResult, axes: tuple[str, ...]) -> float:
    distance = _axis_group_distance(first, second, axes)

    return _distance_to_similarity(distance, max_distance=100.0)


def compute_economic_similarity(first: PersonResult, second: PersonResult) -> float:
    axes = (
        "communisme",
        "capitalisme",
        "regulation",
        "laissez_faire",
        "ecologie",
        "productivisme",
    )
    return _axis_group_similarity(first, second, axes)


def compute_societal_similarity(first: PersonResult, second: PersonResult) -> float:
    axes = (
        "constructivisme",
        "essentialisme",
        "justice_rehabilitative",
        "justice_punitive",
        "progressisme",
        "conservatisme",
        "internationalisme",
        "nationalisme",
    )
    return _axis_group_similarity(first, second, axes)


def _secondary_dimension_differences(
    first: PersonResult,
    second: PersonResult,
) -> tuple[DimensionDifference, ...]:
    first_dimensions = compute_secondary_dimensions(_scores(first))
    second_dimensions = compute_secondary_dimensions(_scores(second))

    dimensions = sorted(set(first_dimensions) | set(second_dimensions))

    differences = [
        DimensionDifference(
            dimension=dimension,
            first_value=round(_as_float(first_dimensions.get(dimension)), 4),
            second_value=round(_as_float(second_dimensions.get(dimension)), 4),
            absolute_gap=round(abs(_as_float(first_dimensions.get(dimension)) - _as_float(second_dimensions.get(dimension))), 4),
        )
        for dimension in dimensions
    ]

    differences.sort(key=lambda item: item.absolute_gap, reverse=True)

    return tuple(differences)


def compute_secondary_similarity(first: PersonResult, second: PersonResult) -> float:
    differences = _secondary_dimension_differences(first, second)

    if not differences:
        return 100.0

    mean_gap = sum(item.absolute_gap for item in differences) / len(differences)

    # Secondary dimensions usually range roughly from -100 to 100.
    # A gap of 200 represents maximum opposition.
    return _distance_to_similarity(mean_gap, max_distance=200.0)


def _strong_axes(person: PersonResult, threshold: float = 65.0) -> set[str]:
    return {axis for axis, value in _scores(person).items() if _as_float(value) >= threshold}


def _weak_axes(person: PersonResult, threshold: float = 35.0) -> set[str]:
    return {axis for axis, value in _scores(person).items() if _as_float(value) <= threshold}


def _largest_axis_gaps(first: PersonResult, second: PersonResult, limit: int = 6) -> tuple[AxisGap, ...]:
    axes = sorted(set(_scores(first)) | set(_scores(second)))

    gaps = [
        AxisGap(
            axis=axis,
            first_score=round(_axis_value(first, axis), 4),
            second_score=round(_axis_value(second, axis), 4),
            absolute_gap=round(abs(_axis_value(first, axis) - _axis_value(second, axis)), 4),
        )
        for axis in axes
    ]

    gaps.sort(key=lambda item: item.absolute_gap, reverse=True)

    return tuple(gaps[:limit])


def _closest_and_most_divergent_dimensions(
    differences: tuple[DimensionDifference, ...],
) -> tuple[str, str]:
    if not differences:
        return "none", "none"

    most_divergent = differences[0].dimension
    closest = min(differences, key=lambda item: item.absolute_gap).dimension

    return closest, most_divergent


def _similarity_label(score: float) -> str:
    if score >= 85:
        return "very close"
    if score >= 70:
        return "close"
    if score >= 50:
        return "partially similar"
    if score >= 30:
        return "distant"
    return "strongly opposed"


def _build_summary(
    first: PersonResult,
    second: PersonResult,
    global_similarity: float,
    economic_similarity: float,
    societal_similarity: float,
    secondary_similarity: float,
    largest_axis_gaps: tuple[AxisGap, ...],
    secondary_gaps: tuple[DimensionDifference, ...],
) -> tuple[str, str]:
    label = _similarity_label(global_similarity)

    main_axis_gap = largest_axis_gaps[0].axis if largest_axis_gaps else "no clear axis"
    main_secondary_gap = secondary_gaps[0].dimension if secondary_gaps else "no clear secondary dimension"

    summary = (
        f"{first.name} and {second.name} are {label} overall "
        f"({global_similarity:.1f}/100 global similarity). "
        f"Their largest direct axis gap is {main_axis_gap}."
    )

    detailed = (
        f"Economic similarity: {economic_similarity:.1f}/100. "
        f"Societal similarity: {societal_similarity:.1f}/100. "
        f"Secondary-dimension similarity: {secondary_similarity:.1f}/100. "
        f"The strongest secondary divergence is {main_secondary_gap}."
    )

    return summary, detailed


def compare_profiles_advanced(first: PersonResult, second: PersonResult) -> AdvancedProfileComparison:
    coordinate_distance = compute_coordinate_distance(first, second)
    global_similarity = compute_global_similarity(first, second)
    economic_similarity = compute_economic_similarity(first, second)
    societal_similarity = compute_societal_similarity(first, second)
    secondary_similarity = compute_secondary_similarity(first, second)

    axis_gaps = _largest_axis_gaps(first, second)
    secondary_gaps = _secondary_dimension_differences(first, second)

    closest_dimension, most_divergent_dimension = _closest_and_most_divergent_dimensions(secondary_gaps)

    shared_dominant = tuple(sorted(_strong_axes(first) & _strong_axes(second)))
    shared_weak = tuple(sorted(_weak_axes(first) & _weak_axes(second)))

    summary, detailed = _build_summary(
        first=first,
        second=second,
        global_similarity=global_similarity,
        economic_similarity=economic_similarity,
        societal_similarity=societal_similarity,
        secondary_similarity=secondary_similarity,
        largest_axis_gaps=axis_gaps,
        secondary_gaps=secondary_gaps,
    )

    return AdvancedProfileComparison(
        first_name=first.name,
        second_name=second.name,
        coordinate_distance=round(coordinate_distance, 4),
        global_similarity_score=global_similarity,
        economic_similarity_score=economic_similarity,
        societal_similarity_score=societal_similarity,
        secondary_similarity_score=secondary_similarity,
        closest_dimension=closest_dimension,
        most_divergent_dimension=most_divergent_dimension,
        shared_dominant_axes=shared_dominant,
        shared_weak_axes=shared_weak,
        largest_axis_gaps=axis_gaps,
        secondary_dimension_gaps=secondary_gaps,
        summary=summary,
        detailed_summary=detailed,
    )


def build_advanced_profile_comparisons(
    people: Iterable[PersonResult],
) -> list[AdvancedProfileComparison]:
    profiles = list(people)

    if len(profiles) < 2:
        return []

    return [compare_profiles_advanced(first, second) for first, second in combinations(profiles, 2)]


def build_advanced_comparison_rows(
    comparisons: Iterable[AdvancedProfileComparison],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for comparison in comparisons:
        rows.append(
            {
                "first_profile": comparison.first_name,
                "second_profile": comparison.second_name,
                "coordinate_distance": comparison.coordinate_distance,
                "global_similarity_score": comparison.global_similarity_score,
                "economic_similarity_score": comparison.economic_similarity_score,
                "societal_similarity_score": comparison.societal_similarity_score,
                "secondary_similarity_score": comparison.secondary_similarity_score,
                "closest_dimension": comparison.closest_dimension,
                "most_divergent_dimension": comparison.most_divergent_dimension,
                "shared_dominant_axes": ", ".join(comparison.shared_dominant_axes),
                "shared_weak_axes": ", ".join(comparison.shared_weak_axes),
                "largest_axis_gaps": ", ".join(gap.axis for gap in comparison.largest_axis_gaps),
                "largest_secondary_gaps": ", ".join(gap.dimension for gap in comparison.secondary_dimension_gaps),
                "summary": comparison.summary,
                "detailed_summary": comparison.detailed_summary,
            }
        )

    return rows


def build_similarity_matrix(people: Iterable[PersonResult]) -> list[dict[str, object]]:
    profiles = list(people)
    rows: list[dict[str, object]] = []

    for first in profiles:
        row: dict[str, object] = {"profile": first.name}

        for second in profiles:
            row[second.name] = compute_global_similarity(first, second)

        rows.append(row)

    return rows
