from pathlib import Path
import csv


DATASET = Path("data/reference/personalities.csv")
AUDIT_CSV = Path("data/reference/profile_coordinate_audit.csv")
AUDIT_MD = Path("docs/reference_dataset_profile_audit.md")


def _rows():
    with DATASET.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def test_reference_dataset_has_no_unknown_gender_values():
    rows = _rows()

    assert rows
    assert {row["gender"].strip().lower() for row in rows} <= {"male", "female"}
    assert "unknown" not in {row["gender"].strip().lower() for row in rows}


def test_reference_dataset_tags_do_not_keep_unknown_gender_after_normalization():
    for row in _rows():
        tags = {tag.strip().lower() for tag in row.get("tags", "").split(";") if tag.strip()}
        assert "unknown" not in tags
        assert row["gender"].strip().lower() in tags


def test_high_confidence_gender_corrections_are_applied():
    rows = {row["name"]: row for row in _rows()}

    expected = {
        "Friedrich Hayek": "male",
        "Hannah Arendt": "female",
        "Ayn Rand": "female",
        "Aung San Suu Kyi": "female",
        "Tawakkol Karman": "female",
        "Amin Maalouf": "male",
    }

    for name, gender in expected.items():
        if name in rows:
            assert rows[name]["gender"].strip().lower() == gender


def test_high_confidence_coordinate_overrides_are_applied():
    rows = {row["name"]: row for row in _rows()}

    expected = {
        "Friedrich Hayek": ("2.8", "-1.3"),
        "Hannah Arendt": ("0.1", "-0.7"),
        "Deng Xiaoping": ("1.0", "2.4"),
        "Xi Jinping": ("0.0", "3.2"),
    }

    for name, coordinates in expected.items():
        if name in rows:
            assert (rows[name]["x"], rows[name]["y"]) == coordinates


def test_coordinate_audit_artifacts_exist():
    assert AUDIT_CSV.exists()
    assert AUDIT_MD.exists()

    content = AUDIT_MD.read_text(encoding="utf-8")
    assert "Reference dataset profile audit" in content
    assert "Coordinate rows flagged for manual review" in content
