from __future__ import annotations

from typing import Iterable

from political_spectrum_analyzer.domain.models import PersonalityPoint


ANY_VALUE = "Any"


def _normalize_filter_value(value: str | None) -> str:
    return (value or ANY_VALUE).strip()


def _split_values(value: str | None) -> list[str]:
    if not value:
        return []

    normalized = str(value).replace("/", ";").replace("|", ";").replace(",", ";")
    return [part.strip() for part in normalized.split(";") if part.strip()]


def _matches_filter(actual_value: str | None, selected_value: str | None) -> bool:
    selected_value = _normalize_filter_value(selected_value)

    if selected_value == ANY_VALUE:
        return True

    actual_values = _split_values(actual_value)

    return any(value.lower() == selected_value.lower() for value in actual_values)


def get_unique_values(
    personalities: Iterable[PersonalityPoint],
    attribute_name: str,
) -> list[str]:
    values = set()

    for personality in personalities:
        raw_value = getattr(personality, attribute_name, None)

        for value in _split_values(raw_value):
            values.add(value)

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