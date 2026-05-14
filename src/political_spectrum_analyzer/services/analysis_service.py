from __future__ import annotations

import math
from typing import Iterable

from political_spectrum_analyzer.domain.models import (
    PersonResult,
    PersonalityPoint,
    ProfileAnalysis,
    ReferenceMatch,
)


CENTER_THRESHOLD = 0.35


def compute_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def compute_distance_to_center(x: float, y: float) -> float:
    return compute_distance(x, y, 0.0, 0.0)


def classify_economic_axis(x: float) -> str:
    if x < -CENTER_THRESHOLD:
        return "Left"
    if x > CENTER_THRESHOLD:
        return "Right"
    return "Center"


def classify_societal_axis(y: float) -> str:
    if y < -CENTER_THRESHOLD:
        return "Libertarian"
    if y > CENTER_THRESHOLD:
        return "Authoritarian"
    return "Moderate"


def get_quadrant(x: float, y: float) -> str:
    economic_position = classify_economic_axis(x)
    societal_position = classify_societal_axis(y)

    if economic_position == "Center" and societal_position == "Moderate":
        return "Center / Moderate"

    return f"{economic_position} / {societal_position}"


def find_closest_references(
    person: PersonResult,
    personalities: Iterable[PersonalityPoint],
    top_n: int = 3,
) -> list[ReferenceMatch]:
    matches: list[ReferenceMatch] = []

    for personality in personalities:
        distance = compute_distance(person.x, person.y, personality.x, personality.y)

        matches.append(
            ReferenceMatch(
                name=personality.name,
                display_group=personality.display_group,
                distance=round(distance, 3),
                x=personality.x,
                y=personality.y,
            )
        )

    return sorted(matches, key=lambda match: match.distance)[:top_n]


def analyze_profile(
    person: PersonResult,
    personalities: Iterable[PersonalityPoint],
    top_n: int = 3,
) -> ProfileAnalysis:
    return ProfileAnalysis(
        name=person.name,
        x=round(person.x, 3),
        y=round(person.y, 3),
        quadrant=get_quadrant(person.x, person.y),
        distance_to_center=round(compute_distance_to_center(person.x, person.y), 3),
        closest_references=find_closest_references(
            person=person,
            personalities=personalities,
            top_n=top_n,
        ),
    )
