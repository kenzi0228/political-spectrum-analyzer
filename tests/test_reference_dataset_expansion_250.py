
import csv
from pathlib import Path

PERSONALITIES = Path("data/reference/personalities.csv")

def _rows() -> list[dict[str, str]]:
    with PERSONALITIES.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def test_reference_dataset_has_250_profiles():
    assert len(_rows()) == 425

def test_reference_dataset_contains_no_duplicate_header_rows():
    for row in _rows():
        assert row["name"].lower() != "name"
        assert row["x"].lower() != "x"
        assert row["ux"].lower() != "ux"

def test_reference_dataset_250_keeps_coordinates_bounded():
    for row in _rows():
        assert -4 <= float(row["x"]) <= 4
        assert -4 <= float(row["y"]) <= 4

def test_reference_dataset_250_has_role_and_country_diversity():
    rows = _rows()
    roles = {row["role_category"] for row in rows if row["role_category"].strip()}
    codes = set()
    for row in rows:
        codes.update(value.strip() for value in row["country_codes"].replace(",", ";").split(";") if value.strip())
    assert len(roles) >= 8
    assert len(codes) >= 35

def test_reference_dataset_250_has_ideological_diversity():
    families = {row["ideology_family"] for row in _rows() if row["ideology_family"].strip()}
    assert len(families) >= 15
