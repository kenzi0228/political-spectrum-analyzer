import csv
from pathlib import Path


PERSONALITIES = Path("data/reference/personalities.csv")


def _rows() -> list[dict[str, str]]:
    with PERSONALITIES.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_reference_dataset_has_350_profiles():
    assert len(_rows()) == 350


def test_reference_dataset_350_includes_new_expansion_profiles():
    names = {row["name"] for row in _rows()}

    expected = {
        "Harriet Tubman",
        "Lucy Parsons",
        "Eugene V. Debs",
        "Kimberlé Crenshaw",
        "Gayatri Spivak",
        "Aimé Césaire",
        "Mother Jones",
        "Dorothy Day",
        "Isaiah Berlin",
        "Jean-Paul Sartre",
    }

    assert expected.issubset(names)


def test_reference_dataset_350_has_no_duplicate_names():
    names = [row["name"].strip().lower() for row in _rows()]

    assert len(names) == len(set(names))


def test_reference_dataset_350_keeps_coordinates_bounded():
    for row in _rows():
        assert -4 <= float(row["x"]) <= 4
        assert -4 <= float(row["y"]) <= 4


def test_reference_dataset_350_has_role_country_and_ideology_diversity():
    rows = _rows()
    roles = {row["role_category"] for row in rows if row["role_category"].strip()}
    families = {row["ideology_family"] for row in rows if row["ideology_family"].strip()}
    codes = set()

    for row in rows:
        codes.update(value.strip() for value in row["country_codes"].replace(",", ";").split(";") if value.strip())

    assert len(roles) >= 8
    assert len(codes) >= 45
    assert len(families) >= 18
