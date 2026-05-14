from __future__ import annotations

from typing import Iterable

from political_spectrum_analyzer.domain.models import PersonalityPoint


ANY_VALUE = "Any"


def _normalize_filter_value(value: str | None) -> str:
    return (value or ANY_VALUE).strip()


def _matches_filter(actual_value: str | None, selected_value: str | None) -> bool:
    selected_value = _normalize_filter_value(selected_value)

    if selected_value == ANY_VALUE:
        return True

    return (actual_value or "").strip().lower() == selected_value.lower()


def get_unique_values(
    personalities: Iterable[PersonalityPoint],
    attribute_name: str,
) -> list[str]:
    values = set()

    for personality in personalities:
        value = getattr(personality, attribute_name, None)

        if value:
            values.add(str(value).strip())

    return [ANY_VALUE] + sorted(values)


def filter_personalities(
    personalities: Iterable[PersonalityPoint],
    display_group: str | None = ANY_VALUE,
    country: str | None = ANY_VALUE,
    period: str | None = ANY_VALUE,
    ideology_family: str | None = ANY_VALUE,
) -> list[PersonalityPoint]:
    filtered: list[PersonalityPoint] = []

    for personality in personalities:
        if not _matches_filter(personality.display_group, display_group):
            continue

        if not _matches_filter(personality.country, country):
            continue

        if not _matches_filter(personality.period, period):
            continue

        if not _matches_filter(personality.ideology_family, ideology_family):
            continue

        filtered.append(personality)

    return filtered