import csv
from collections import Counter
from pathlib import Path


PERSONALITIES = Path("data/reference/personalities.csv")
QUALITY_DOC = Path("docs/reference_dataset_quality_rules_v2.md")

REQUIRED_COLUMNS = {
    "name",
    "display_group",
    "country",
    "country_codes",
    "period",
    "century",
    "ideology_family",
    "ideology_subtype",
    "role_category",
    "x",
    "y",
    "ux",
    "uy",
    "confidence",
    "is_estimated",
    "source",
    "notes",
    "tags",
}

VALID_CONFIDENCE = {"low", "medium", "high"}
VALID_ESTIMATED = {"true", "false", "yes", "no", "1", "0"}


def _rows() -> list[dict[str, str]]:
    with PERSONALITIES.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _split_multi(value: str) -> list[str]:
    return [item.strip() for item in str(value or "").replace(",", ";").split(";") if item.strip()]


def test_quality_rules_v2_dataset_has_expected_size_for_current_stage():
    rows = _rows()

    assert len(rows) == 350


def test_quality_rules_v2_required_columns_exist_and_region_is_absent():
    rows = _rows()

    assert rows
    assert REQUIRED_COLUMNS.issubset(rows[0].keys())
    assert "region" not in rows[0].keys()


def test_quality_rules_v2_names_are_unique():
    rows = _rows()
    names = [row["name"].strip().lower() for row in rows]

    duplicates = [name for name, count in Counter(names).items() if count > 1]

    assert not duplicates


def test_quality_rules_v2_core_fields_are_populated():
    rows = _rows()

    required_non_empty = [
        "name",
        "display_group",
        "country",
        "country_codes",
        "period",
        "century",
        "ideology_family",
        "ideology_subtype",
        "role_category",
        "confidence",
        "notes",
        "tags",
    ]

    for row in rows:
        for column in required_non_empty:
            assert row[column].strip(), f"{row.get('name', '<unknown>')} has empty {column}"


def test_quality_rules_v2_coordinate_bounds_are_valid():
    rows = _rows()

    for row in rows:
        x = float(row["x"])
        y = float(row["y"])

        assert -4.0 <= x <= 4.0
        assert -4.0 <= y <= 4.0


def test_quality_rules_v2_uncertainty_values_are_positive():
    rows = _rows()

    for row in rows:
        ux = float(row["ux"])
        uy = float(row["uy"])

        assert ux > 0
        assert uy > 0


def test_quality_rules_v2_confidence_values_are_controlled():
    rows = _rows()

    for row in rows:
        assert row["confidence"].strip().lower() in VALID_CONFIDENCE


def test_quality_rules_v2_estimated_values_are_boolean_like():
    rows = _rows()

    for row in rows:
        assert row["is_estimated"].strip().lower() in VALID_ESTIMATED


def test_quality_rules_v2_country_codes_are_semicolon_friendly_and_non_empty():
    rows = _rows()

    unique_codes = set()

    for row in rows:
        codes = _split_multi(row["country_codes"])
        assert codes

        for code in codes:
            assert len(code) == 3 or code in {"UNK", "SUN", "YUG", "CSK"}
            unique_codes.add(code)

    assert len(unique_codes) >= 20


def test_quality_rules_v2_century_values_are_diverse():
    rows = _rows()
    centuries = set()

    for row in rows:
        centuries.update(_split_multi(row["century"]))

    assert len(centuries) >= 3
    assert any("20th century" == century for century in centuries)


def test_quality_rules_v2_role_categories_are_diverse():
    rows = _rows()
    roles = {row["role_category"].strip() for row in rows if row["role_category"].strip()}

    assert len(roles) >= 6


def test_quality_rules_v2_ideology_families_are_filterable():
    rows = _rows()
    families = {row["ideology_family"].strip() for row in rows if row["ideology_family"].strip()}

    assert 8 <= len(families) <= 45


def test_quality_rules_v2_tags_include_filtering_metadata():
    rows = _rows()

    for row in rows:
        tags = set(_split_multi(row["tags"]))

        assert row["ideology_family"] in tags
        assert row["role_category"] in tags or row["display_group"] in tags


def test_quality_rules_v2_documentation_exists():
    content = QUALITY_DOC.read_text(encoding="utf-8")

    assert "Reference dataset quality rules v2" in content
    assert "no duplicate names" in content
    assert "500 profiles" in content


def test_readme_mentions_quality_rules_v2():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Reference dataset quality rules v2" in content
    assert "valid coordinate bounds" in content
    assert "500 reference profiles" in content
