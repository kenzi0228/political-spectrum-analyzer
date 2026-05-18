
import csv
from pathlib import Path

PERSONALITIES = Path("data/reference/personalities.csv")
TAXONOMY = Path("data/reference/ideology_taxonomy.csv")
SOURCES = Path("data/reference/reference_sources.csv")
SCHEMA_DOC = Path("docs/reference_dataset_schema_v2.md")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_reference_dataset_schema_v2_columns_exist_without_region():
    rows = _rows(PERSONALITIES)
    assert rows
    required_columns = {
        "name", "display_group", "country", "country_codes", "period", "century",
        "ideology_family", "ideology_subtype", "role_category", "x", "y", "ux",
        "uy", "confidence", "is_estimated", "source", "notes", "tags",
    }
    assert required_columns.issubset(rows[0].keys())
    assert "region" not in rows[0].keys()


def test_reference_dataset_schema_v2_fields_are_populated():
    rows = _rows(PERSONALITIES)
    for row in rows:
        assert row["country"].strip()
        assert row["country_codes"].strip()
        assert row["century"].strip()
        assert row["ideology_family"].strip()
        assert row["ideology_subtype"].strip()
        assert row["role_category"].strip()
        assert row["tags"].strip()


def test_reference_dataset_schema_v2_preserves_dataset_size():
    rows = _rows(PERSONALITIES)
    assert len(rows) == 250


def test_ideology_family_count_is_filterable_not_excessive():
    rows = _rows(PERSONALITIES)
    families = {row["ideology_family"] for row in rows if row["ideology_family"].strip()}
    assert 8 <= len(families) <= 45


def test_ideology_taxonomy_exists_and_documents_families():
    rows = _rows(TAXONOMY)
    assert rows
    assert {"ideology_family", "description", "accepted_subtypes"}.issubset(rows[0].keys())
    assert len(rows) >= 10


def test_reference_sources_file_exists():
    with SOURCES.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        assert {"name", "source_type", "source_reference", "reliability_note"}.issubset(reader.fieldnames or [])


def test_schema_documentation_exists_without_region():
    content = SCHEMA_DOC.read_text(encoding="utf-8")
    assert "Reference dataset schema v2" in content
    assert "ideology_taxonomy.csv" in content
    assert "500 profiles" in content
    assert "does not include a `region` field" in content


def test_readme_mentions_reference_dataset_schema_v2_without_region():
    content = Path("README.md").read_text(encoding="utf-8")
    assert "Reference dataset schema v2" in content
    assert "ideology_taxonomy.csv" in content
    assert "500 profiles" in content
    assert "avoids a `region` column" in content
