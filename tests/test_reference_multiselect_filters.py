
from political_spectrum_analyzer.services.personality_filter_service import (
    filter_reference_items_multiselect,
    matches_multiselect_filter,
    split_filter_values,
)

ITEMS = [
    {
        "name": "A",
        "country": "France; Algeria",
        "country_codes": "FRA; DZA",
        "ideology_family": "Socialism",
        "ideology_subtype": "Democratic socialism",
        "role_category": "Thinker",
        "century": "20th century",
        "display_group": "Philosopher",
        "tags": "Thinker; Socialism; FRA; DZA",
    },
    {
        "name": "B",
        "country": "United States",
        "country_codes": "USA",
        "ideology_family": "Liberalism",
        "ideology_subtype": "Classical liberalism",
        "role_category": "Economist",
        "century": "18th century",
        "display_group": "Economist",
        "tags": "Economist; Liberalism; USA",
    },
]


def test_split_filter_values_supports_semicolon_and_comma():
    assert split_filter_values("France; Algeria, Tunisia") == ["France", "Algeria", "Tunisia"]


def test_matches_multiselect_filter_accepts_empty_as_any():
    assert matches_multiselect_filter(ITEMS[0], "country", [])


def test_matches_multiselect_filter_supports_multi_country_entries():
    assert matches_multiselect_filter(ITEMS[0], "country", ["Algeria"])
    assert matches_multiselect_filter(ITEMS[0], "country_codes", ["DZA"])


def test_filter_reference_items_multiselect_combines_filters():
    filtered = filter_reference_items_multiselect(
        ITEMS,
        countries=["France"],
        ideology_families=["Socialism"],
        role_categories=["Thinker"],
    )
    assert [item["name"] for item in filtered] == ["A"]


def test_filter_reference_items_multiselect_supports_multiple_choices():
    filtered = filter_reference_items_multiselect(
        ITEMS,
        ideology_families=["Socialism", "Liberalism"],
    )
    assert {item["name"] for item in filtered} == {"A", "B"}
