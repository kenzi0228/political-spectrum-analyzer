import csv
from pathlib import Path


TAXONOMY = Path("data/reference/ideology_taxonomy.csv")
ALIASES = Path("data/reference/ideology_aliases.csv")
PERSONALITIES = Path("data/reference/personalities.csv")
DOC = Path("docs/ideology_taxonomy.md")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_ideology_taxonomy_v2_columns_exist():
    rows = _rows(TAXONOMY)

    assert rows
    assert {
        "ideology_family",
        "description",
        "accepted_subtypes",
        "aliases",
        "analysis_guidance",
    }.issubset(rows[0].keys())


def test_ideology_taxonomy_v2_has_no_duplicate_families():
    rows = _rows(TAXONOMY)
    families = [row["ideology_family"] for row in rows]

    assert len(families) == len(set(families))


def test_ideology_taxonomy_v2_has_expected_core_families():
    rows = _rows(TAXONOMY)
    families = {row["ideology_family"] for row in rows}

    expected = {
        "Liberalism",
        "Conservatism",
        "Socialism",
        "Communism",
        "Social democracy",
        "Anarchism",
        "Libertarianism",
        "Nationalism",
        "Fascism",
        "Republicanism",
        "Centrism",
        "Ecologism",
        "Anti-colonialism",
        "Populism",
        "Political religion",
        "Technocracy",
        "Monarchism",
        "Authoritarianism",
    }

    assert expected.issubset(families)


def test_ideology_taxonomy_v2_entries_are_documented():
    rows = _rows(TAXONOMY)

    for row in rows:
        assert row["description"].strip()
        assert row["accepted_subtypes"].strip()
        assert row["aliases"].strip()
        assert row["analysis_guidance"].strip()


def test_ideology_aliases_map_to_known_families():
    taxonomy_families = {row["ideology_family"] for row in _rows(TAXONOMY)}
    alias_rows = _rows(ALIASES)

    assert alias_rows

    for row in alias_rows:
        assert row["alias"].strip()
        assert row["ideology_family"] in taxonomy_families


def test_personality_ideology_families_are_covered_by_taxonomy():
    taxonomy_families = {row["ideology_family"] for row in _rows(TAXONOMY)}
    personality_families = {
        row["ideology_family"]
        for row in _rows(PERSONALITIES)
        if row["ideology_family"].strip()
    }

    missing = sorted(personality_families - taxonomy_families - {"Unclassified"})

    assert not missing, f"Missing ideology families in taxonomy: {missing}"


def test_ideology_taxonomy_documentation_exists():
    content = DOC.read_text(encoding="utf-8")

    assert "Ideology taxonomy v2" in content
    assert "ideology_family" in content
    assert "ideology_subtype" in content
    assert "500 profiles" in content


def test_readme_mentions_ideology_taxonomy_v2():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Ideology taxonomy v2" in content
    assert "data/reference/ideology_taxonomy.csv" in content
    assert "data/reference/ideology_aliases.csv" in content
