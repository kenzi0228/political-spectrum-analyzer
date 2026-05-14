from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Literal

from political_spectrum_analyzer.domain.models import PersonResult, PersonalityPoint
from political_spectrum_analyzer.services.analysis_service import (
    analyze_profile,
    compute_distance,
)


ReferenceExportMode = Literal[
    "profiles_only",
    "closest_references",
    "all_references",
    "filtered_references",
]


EXPORT_FIELDNAMES = [
    "record_type",
    "profile_name",
    "profile_x",
    "profile_y",
    "quadrant",
    "distance_to_center",
    "reference_rank",
    "reference_name",
    "reference_group",
    "reference_x",
    "reference_y",
    "reference_distance",
]


def _round(value: float) -> float:
    return round(float(value), 3)


def _profile_row(person: PersonResult, personalities: Iterable[PersonalityPoint]) -> dict[str, object]:
    analysis = analyze_profile(person=person, personalities=personalities, top_n=3)

    return {
        "record_type": "profile",
        "profile_name": analysis.name,
        "profile_x": analysis.x,
        "profile_y": analysis.y,
        "quadrant": analysis.quadrant,
        "distance_to_center": analysis.distance_to_center,
        "reference_rank": "",
        "reference_name": "",
        "reference_group": "",
        "reference_x": "",
        "reference_y": "",
        "reference_distance": "",
    }


def _reference_row(
    person: PersonResult,
    reference: PersonalityPoint,
    rank: int | str,
) -> dict[str, object]:
    return {
        "record_type": "reference",
        "profile_name": person.name,
        "profile_x": _round(person.x),
        "profile_y": _round(person.y),
        "quadrant": "",
        "distance_to_center": "",
        "reference_rank": rank,
        "reference_name": reference.name,
        "reference_group": reference.display_group,
        "reference_x": _round(reference.x),
        "reference_y": _round(reference.y),
        "reference_distance": _round(compute_distance(person.x, person.y, reference.x, reference.y)),
    }


def build_export_rows(
    people: Iterable[PersonResult],
    personalities: Iterable[PersonalityPoint],
    mode: ReferenceExportMode = "profiles_only",
    closest_count: int = 3,
    filtered_personalities: Iterable[PersonalityPoint] | None = None,
) -> list[dict[str, object]]:
    people_list = list(people)
    personalities_list = list(personalities)
    filtered_personalities_list = list(filtered_personalities or [])

    rows: list[dict[str, object]] = []

    for person in people_list:
        rows.append(_profile_row(person, personalities_list))

        if mode == "profiles_only":
            continue

        if mode == "closest_references":
            analysis = analyze_profile(
                person=person,
                personalities=personalities_list,
                top_n=closest_count,
            )

            reference_by_name = {reference.name: reference for reference in personalities_list}

            for rank, match in enumerate(analysis.closest_references, start=1):
                reference = reference_by_name.get(match.name)

                if reference is None:
                    continue

                rows.append(_reference_row(person, reference, rank))

        elif mode == "all_references":
            sorted_references = sorted(
                personalities_list,
                key=lambda reference: compute_distance(person.x, person.y, reference.x, reference.y),
            )

            for rank, reference in enumerate(sorted_references, start=1):
                rows.append(_reference_row(person, reference, rank))

        elif mode == "filtered_references":
            sorted_references = sorted(
                filtered_personalities_list,
                key=lambda reference: compute_distance(person.x, person.y, reference.x, reference.y),
            )

            for rank, reference in enumerate(sorted_references, start=1):
                rows.append(_reference_row(person, reference, rank))

        else:
            raise ValueError(f"Unknown export mode: {mode}")

    return rows


def export_analysis_to_csv(
    file_path: str | Path,
    people: Iterable[PersonResult],
    personalities: Iterable[PersonalityPoint],
    mode: ReferenceExportMode = "profiles_only",
    closest_count: int = 3,
    filtered_personalities: Iterable[PersonalityPoint] | None = None,
) -> Path:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = build_export_rows(
        people=people,
        personalities=personalities,
        mode=mode,
        closest_count=closest_count,
        filtered_personalities=filtered_personalities,
    )

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=EXPORT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    return path