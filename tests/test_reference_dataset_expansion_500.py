import csv
from pathlib import Path


PERSONALITIES = Path("data/reference/personalities.csv")
SUMMARY = Path("data/reference/reference_dataset_summary.csv")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _summary() -> dict[str, str]:
    return {row["metric"]: row["value"] for row in _rows(SUMMARY)}


def test_reference_dataset_has_500_profiles():
    assert len(_rows(PERSONALITIES)) == 500


def test_reference_dataset_500_has_no_duplicate_header_rows():
    for row in _rows(PERSONALITIES):
        assert row["name"].lower() != "name"
        assert row["x"].lower() != "x"
        assert row["ux"].lower() != "ux"
        assert row["country_codes"].lower() != "country_codes"


def test_reference_dataset_500_has_normalized_gender_values():
    allowed = {"male", "female", "unknown"}
    genders = {row["gender"] for row in _rows(PERSONALITIES)}

    assert genders.issubset(allowed)
    assert {"male", "female"}.issubset(genders)


def test_reference_dataset_500_summary_matches_size():
    summary = _summary()

    assert int(summary["profile_count"]) == 500


def test_reference_dataset_500_has_no_duplicate_names():
    names = [row["name"].strip().lower() for row in _rows(PERSONALITIES)]

    assert len(names) == len(set(names))
