from __future__ import annotations

from typing import Iterable

from political_spectrum_analyzer.domain.models import PersonalityPoint


NONE_VALUE = "None"
ANY_VALUE = "Any"

# Backward-compatible alias used by older UI/tests if needed.
NO_FILTER_VALUE = NONE_VALUE


def _normalize_filter_value(value: str | None) -> str:
    return (value or NONE_VALUE).strip()


def _split_values(value: str | None) -> list[str]:
    if not value:
        return []

    normalized = str(value).replace("/", ";").replace("|", ";").replace(",", ";")
    return [part.strip() for part in normalized.split(";") if part.strip()]


def _is_inactive_filter(value: str | None) -> bool:
    normalized = _normalize_filter_value(value)
    return normalized in {NONE_VALUE, ANY_VALUE}


def _has_explicit_filter_selection(*values: str | None) -> bool:
    """
    Return True when the user explicitly asked to display references.

    Semantics:
    - all filters = None -> display no references by default
    - at least one filter = Any -> display references without restricting that dimension
    - at least one concrete value -> display matching references
    """
    return any(_normalize_filter_value(value) != NONE_VALUE for value in values)


def _matches_filter(actual_value: str | None, selected_value: str | None) -> bool:
    selected_value = _normalize_filter_value(selected_value)

    if selected_value in {NONE_VALUE, ANY_VALUE}:
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

    return [NONE_VALUE, ANY_VALUE] + sorted(values)


def filter_personalities(
    personalities: Iterable[PersonalityPoint],
    display_group: str | None = NONE_VALUE,
    country: str | None = NONE_VALUE,
    period: str | None = NONE_VALUE,
    ideology_family: str | None = NONE_VALUE,
) -> list[PersonalityPoint]:
    """
    Filter reference personalities.

    UI semantics:
    - None on every filter means: show no reference personalities.
    - Any means: show all values for that dimension.
    - A concrete value means: restrict to that value.
    - Mixed filters are supported, e.g. Group=President, Country=None.
    """
    if not _has_explicit_filter_selection(
        display_group,
        country,
        period,
        ideology_family,
    ):
        return []

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

# ---------------------------------------------------------------------------
# Multi-select reference filtering helpers
# ---------------------------------------------------------------------------

def split_filter_values(value):
    """Split semicolon/comma-separated filter values into normalized tokens."""

    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        items = []
        for item in value:
            items.extend(split_filter_values(item))
        return items

    return [
        item.strip()
        for item in str(value).replace(",", ";").split(";")
        if item and item.strip()
    ]


def _get_field_value(item, field_name):
    if isinstance(item, dict):
        return item.get(field_name, "")
    return getattr(item, field_name, "")


def matches_multiselect_filter(item, field_name, selected_values):
    """Return True when an item matches a multi-select filter."""

    selected = [str(value).strip() for value in (selected_values or []) if str(value).strip()]

    if not selected:
        return True

    lowered_selected = {value.lower() for value in selected}

    if lowered_selected & {"any", "all", "tous", "all values"}:
        return True

    field_value = _get_field_value(item, field_name)
    field_tokens = {value.lower() for value in split_filter_values(field_value)}

    if "none" in lowered_selected:
        return not field_tokens

    return bool(field_tokens & lowered_selected)


def filter_reference_items_multiselect(
    items,
    *,
    countries=None,
    country_codes=None,
    ideology_families=None,
    ideology_subtypes=None,
    role_categories=None,
    centuries=None,
    display_groups=None,
    tags=None,
):
    """Filter reference personalities using independent multi-select filters."""

    filtered = []

    for item in items:
        if not matches_multiselect_filter(item, "country", countries):
            continue
        if not matches_multiselect_filter(item, "country_codes", country_codes):
            continue
        if not matches_multiselect_filter(item, "ideology_family", ideology_families):
            continue
        if not matches_multiselect_filter(item, "ideology_subtype", ideology_subtypes):
            continue
        if not matches_multiselect_filter(item, "role_category", role_categories):
            continue
        if not matches_multiselect_filter(item, "century", centuries):
            continue
        if not matches_multiselect_filter(item, "display_group", display_groups):
            continue
        if not matches_multiselect_filter(item, "tags", tags):
            continue

        filtered.append(item)

    return filtered
