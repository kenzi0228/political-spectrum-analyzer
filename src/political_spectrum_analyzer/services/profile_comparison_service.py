from __future__ import annotations

from political_spectrum_analyzer.services.advanced_profile_comparison_service import build_advanced_comparison_rows, build_advanced_profile_comparisons, build_similarity_matrix, compare_profiles_advanced

from dataclasses import dataclass
from itertools import combinations
from math import sqrt
from typing import Iterable, Mapping, Sequence

from political_spectrum_analyzer.domain.models import PersonResult


@dataclass(frozen=True)
class AxisDifference:
    axis: str
    first_score: float
    second_score: float
    absolute_gap: float


@dataclass(frozen=True)
class ProfileComparison:
    first_name: str
    second_name: str
    coordinate_distance: float
    ideological_similarity_score: float
    shared_strong_axes: tuple[str, ...]
    shared_weak_axes: tuple[str, ...]
    largest_score_gaps: tuple[AxisDifference, ...]
    summary: str


def _as_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def compute_coordinate_distance(first: PersonResult, second: PersonResult) -> float:
    return sqrt((first.x - second.x) ** 2 + (first.y - second.y) ** 2)


def compute_similarity_score(distance: float, max_distance: float = 8.0) -> float:
    if max_distance <= 0:
        raise ValueError("max_distance must be positive")

    similarity = 100.0 * (1.0 - min(distance, max_distance) / max_distance)

    return round(max(0.0, min(100.0, similarity)), 2)


def _axis_items(scores: Mapping[str, object]) -> dict[str, float]:
    return {axis: _as_float(value) for axis, value in scores.items()}


def _strong_axes(scores: Mapping[str, object], threshold: float = 65.0) -> set[str]:
    return {axis for axis, value in _axis_items(scores).items() if value >= threshold}


def _weak_axes(scores: Mapping[str, object], threshold: float = 35.0) -> set[str]:
    return {axis for axis, value in _axis_items(scores).items() if value <= threshold}


def _largest_score_gaps(
    first_scores: Mapping[str, object],
    second_scores: Mapping[str, object],
    limit: int = 5,
) -> tuple[AxisDifference, ...]:
    axes = sorted(set(first_scores) | set(second_scores))
    differences = [
        AxisDifference(
            axis=axis,
            first_score=_as_float(first_scores.get(axis)),
            second_score=_as_float(second_scores.get(axis)),
            absolute_gap=abs(_as_float(first_scores.get(axis)) - _as_float(second_scores.get(axis))),
        )
        for axis in axes
    ]

    differences.sort(key=lambda item: item.absolute_gap, reverse=True)

    return tuple(differences[:limit])


def _build_summary(
    first: PersonResult,
    second: PersonResult,
    distance: float,
    similarity: float,
    shared_strong_axes: Sequence[str],
    largest_gaps: Sequence[AxisDifference],
) -> str:
    if similarity >= 80:
        proximity = "very close"
    elif similarity >= 60:
        proximity = "fairly close"
    elif similarity >= 40:
        proximity = "moderately distant"
    else:
        proximity = "strongly different"

    shared_text = ", ".join(shared_strong_axes[:3]) if shared_strong_axes else "no major shared dominant axis"
    gap_text = ", ".join(gap.axis for gap in largest_gaps[:3]) if largest_gaps else "no major score gap"

    return (
        f"{first.name} and {second.name} are {proximity} on the political map "
        f"(distance {distance:.2f}, similarity {similarity:.1f}/100). "
        f"Their strongest common points are: {shared_text}. "
        f"The main differences are concentrated around: {gap_text}."
    )


def compare_profiles(first: PersonResult, second: PersonResult) -> ProfileComparison:
    distance = compute_coordinate_distance(first, second)
    similarity = compute_similarity_score(distance)

    shared_strong_axes = tuple(sorted(_strong_axes(first.scores) & _strong_axes(second.scores)))
    shared_weak_axes = tuple(sorted(_weak_axes(first.scores) & _weak_axes(second.scores)))
    largest_gaps = _largest_score_gaps(first.scores, second.scores)

    summary = _build_summary(
        first=first,
        second=second,
        distance=distance,
        similarity=similarity,
        shared_strong_axes=shared_strong_axes,
        largest_gaps=largest_gaps,
    )

    return ProfileComparison(
        first_name=first.name,
        second_name=second.name,
        coordinate_distance=round(distance, 4),
        ideological_similarity_score=similarity,
        shared_strong_axes=shared_strong_axes,
        shared_weak_axes=shared_weak_axes,
        largest_score_gaps=largest_gaps,
        summary=summary,
    )


def build_profile_comparisons(people: Iterable[PersonResult]) -> list[ProfileComparison]:
    profiles = list(people)

    if len(profiles) < 2:
        return []

    return [compare_profiles(first, second) for first, second in combinations(profiles, 2)]


def build_comparison_rows(comparisons: Iterable[ProfileComparison]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for comparison in comparisons:
        rows.append(
            {
                "first_profile": comparison.first_name,
                "second_profile": comparison.second_name,
                "coordinate_distance": comparison.coordinate_distance,
                "ideological_similarity_score": comparison.ideological_similarity_score,
                "shared_strong_axes": ", ".join(comparison.shared_strong_axes),
                "shared_weak_axes": ", ".join(comparison.shared_weak_axes),
                "largest_score_gaps": ", ".join(gap.axis for gap in comparison.largest_score_gaps),
                "summary": comparison.summary,
            }
        )

    return rows