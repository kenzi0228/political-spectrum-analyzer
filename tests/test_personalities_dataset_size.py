import csv
from political_spectrum_analyzer.config import PERSONALITIES_CSV_PATH
from political_spectrum_analyzer.services.personalities_service import load_personalities


def test_personalities_dataset_has_150_entries():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)
    assert len(personalities) == 250


def test_personalities_dataset_has_unique_names():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)
    names = [person.name for person in personalities]
    assert len(names) == len(set(names))


def test_personalities_dataset_required_metadata_is_present():
    with open(PERSONALITIES_CSV_PATH, newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    required_columns = {
        "name",
        "display_group",
        "country",
        "period",
        "ideology_family",
        "x",
        "y",
        "ux",
        "uy",
        "confidence",
        "is_estimated",
        "source",
        "notes",
    }

    assert required_columns.issubset(rows[0].keys())

    for row in rows:
        assert row["name"].strip()
        assert row["display_group"].strip()
        assert row["country"].strip()
        assert row["period"].strip()
        assert row["ideology_family"].strip()
        assert row["notes"].strip()