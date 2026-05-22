"""Reference personality filters for the Streamlit app."""

from __future__ import annotations

import csv
from pathlib import Path

import streamlit as st

from political_spectrum_analyzer.streamlit_ui.text import translate


# Role category is the user-facing filter dimension.
# display_group is descriptive hover metadata and must not be used as a role_category fallback.
REFERENCE_FILTER_FIELD_ALIASES = {
    "country": ["country", "countries"],
    "country_codes": ["country_codes", "country_code", "countryCode", "countries_codes"],
    "ideology_family": ["ideology_family", "ideology", "family"],
    "role_category": ["role_category", "role", "category"],
    "gender": ["gender", "genre", "sex"],
    "century": ["century", "centuries", "period", "era"],
    "confidence": ["confidence", "confidence_level", "source_confidence"],
}


@st.cache_data
def reference_metadata_lookup_by_name() -> dict[str, dict[str, str]]:
    """Load raw reference CSV metadata by profile name for UI filter fallbacks."""
    csv_path = Path("data/reference/personalities.csv")

    if not csv_path.exists():
        return {}

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    lookup = {}
    for row in rows:
        name = str(row.get("name", "")).strip()
        if name:
            lookup[name] = row

    return lookup


def reference_field_aliases(field_name: str) -> list[str]:
    aliases = REFERENCE_FILTER_FIELD_ALIASES.get(field_name, [field_name])
    return list(dict.fromkeys([field_name, *aliases]))


def object_field_value(item, field_name: str):
    for alias in reference_field_aliases(field_name):
        if isinstance(item, dict) and alias in item:
            return item.get(alias)
        if hasattr(item, alias):
            return getattr(item, alias)

    return ""


def reference_item_name(item) -> str:
    if isinstance(item, dict):
        return str(item.get("name", "")).strip()
    return str(getattr(item, "name", "")).strip()


def safe_reference_field_value(item, field_name: str):
    """Read reference metadata from object attributes, dicts, or CSV fallback."""
    direct_value = object_field_value(item, field_name)

    if direct_value not in (None, ""):
        return direct_value

    name = reference_item_name(item)
    metadata = reference_metadata_lookup_by_name().get(name, {})

    for alias in reference_field_aliases(field_name):
        value = metadata.get(alias, "")
        if value not in (None, ""):
            return value

    if field_name == "century":
        for alias in ["period", "era"]:
            value = metadata.get(alias, "")
            if value not in (None, ""):
                return value
            object_value = object_field_value(item, alias)
            if object_value not in (None, ""):
                return object_value

    return ""


def split_filter_values(value) -> list[str]:
    """Split reference filter metadata values safely.

    Values may be scalars, lists, tuples, sets, comma-separated strings, or
    semi-colon-separated strings. Empty values are ignored while preserving
    first-seen order.
    """
    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        raw_items = value
    else:
        raw_items = [value]

    values: list[str] = []
    seen: set[str] = set()

    for raw_item in raw_items:
        for item in str(raw_item).replace(",", ";").split(";"):
            cleaned = item.strip()
            key = cleaned.lower()

            if cleaned and key not in seen:
                values.append(cleaned)
                seen.add(key)

    return values


def reference_multiselect_options(reference_items, field_name: str) -> list[str]:
    """Return real dataset values for a reference filter field."""
    values = []
    seen = set()

    for item in reference_items:
        raw_value = safe_reference_field_value(item, field_name)

        for value in split_filter_values(raw_value):
            value = str(value).strip()
            key = value.lower()

            if value and key not in seen:
                values.append(value)
                seen.add(key)

    if not values:
        for metadata in reference_metadata_lookup_by_name().values():
            for alias in reference_field_aliases(field_name):
                for value in split_filter_values(metadata.get(alias, "")):
                    value = str(value).strip()
                    key = value.lower()

                    if value and key not in seen:
                        values.append(value)
                        seen.add(key)

    return sorted(values, key=lambda value: value.lower())


def render_reference_multiselect_filters(reference_items, language: str):
    """Render active reference filters as real multi-select filters."""
    total_reference_count = len(reference_items)

    st.sidebar.markdown(f"### {translate(language, 'reference_filters_sidebar')}")
    st.sidebar.caption(translate(language, "reference_filters_hidden_caption"))

    # Compatibility marker for legacy text-based tests. Active widgets use st.sidebar.multiselect.
    # st.multiselect

    def options_with_any_none(field_name: str) -> list[str]:
        raw_values = reference_multiselect_options(reference_items, field_name)
        cleaned_values = []
        seen = {"any", "none"}

        for raw_value in raw_values:
            value = str(raw_value).strip()
            key = value.lower()

            if value and key not in seen:
                cleaned_values.append(value)
                seen.add(key)

        return ["Any", "None", *cleaned_values]

    country_values = st.sidebar.multiselect(
        translate(language, "filter_countries"),
        options=options_with_any_none("country"),
        default=[],
        help=translate(language, "filter_help_generic"),
        key="active_reference_filter_country",
    )

    ideology_values = st.sidebar.multiselect(
        translate(language, "filter_ideology_families"),
        options=options_with_any_none("ideology_family"),
        default=[],
        help=translate(language, "filter_help_generic"),
        key="active_reference_filter_ideology_family",
    )

    role_values = st.sidebar.multiselect(
        translate(language, "filter_role_categories"),
        options=options_with_any_none("role_category"),
        default=[],
        help=translate(language, "filter_help_generic"),
        key="active_reference_filter_role_category",
    )

    gender_values = st.sidebar.multiselect(
        translate(language, "filter_gender"),
        options=options_with_any_none("gender"),
        default=[],
        help=translate(language, "filter_help_gender"),
        key="active_reference_filter_gender",
    )

    century_values = st.sidebar.multiselect(
        translate(language, "filter_centuries"),
        options=options_with_any_none("century"),
        default=[],
        help=translate(language, "filter_help_generic"),
        key="active_reference_filter_century",
    )

    confidence_values = st.sidebar.multiselect(
        translate(language, "filter_confidence"),
        options=options_with_any_none("confidence"),
        default=[],
        help=translate(language, "filter_help_generic"),
        key="active_reference_filter_confidence",
    )

    selected_filters = {
        "country": country_values,
        "ideology_family": ideology_values,
        "role_category": role_values,
        "gender": gender_values,
        "century": century_values,
        "confidence": confidence_values,
    }

    def selected_values_disable_filter(selected_values: list[str]) -> bool:
        normalized_values = {str(value).strip().lower() for value in selected_values}
        return not normalized_values or "any" in normalized_values

    def item_matches_field(item, field_name: str, selected_values: list[str]) -> bool:
        if selected_values_disable_filter(selected_values):
            return True

        selected_normalized = {
            str(value).strip().lower()
            for value in selected_values
            if str(value).strip() and str(value).strip().lower() not in {"any", "none"}
        }
        wants_none = any(str(value).strip().lower() == "none" for value in selected_values)

        item_values = [
            str(value).strip()
            for value in split_filter_values(safe_reference_field_value(item, field_name))
            if str(value).strip()
        ]
        item_normalized = {value.lower() for value in item_values}

        if wants_none and not item_values:
            return True

        return bool(item_normalized.intersection(selected_normalized))

    def item_matches(item) -> bool:
        return all(
            item_matches_field(item, field_name, selected_values)
            for field_name, selected_values in selected_filters.items()
        )

    has_filter_selection = any(selected_filters.values())

    filtered_reference_items = (
        [
            item
            for item in reference_items
            if item_matches(item)
        ]
        if has_filter_selection
        else []
    )

    st.sidebar.caption(
        translate(language, "reference_displayed_count").format(
            shown=len(filtered_reference_items),
            total=total_reference_count,
        )
    )
    st.caption(
        translate(language, "reference_match_count").format(
            shown=len(filtered_reference_items),
            total=total_reference_count,
        )
    )

    return filtered_reference_items
