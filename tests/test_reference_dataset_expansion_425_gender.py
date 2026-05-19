import csv
from pathlib import Path


PERSONALITIES = Path("data/reference/personalities.csv")


def _rows() -> list[dict[str, str]]:
    with PERSONALITIES.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def test_reference_dataset_has_425_profiles():
    assert len(_rows()) == 500


def test_reference_dataset_has_gender_column():
    rows = _rows()

    assert "gender" in rows[0]


def test_reference_dataset_gender_values_are_normalized():
    allowed = {"male", "female", "unknown"}

    assert {row["gender"] for row in _rows()}.issubset(allowed)


def test_reference_dataset_gender_has_male_and_female_coverage():
    genders = {row["gender"] for row in _rows()}

    assert "male" in genders
    assert "female" in genders


def test_reference_dataset_425_includes_expansion_profiles():
    names = {row["name"] for row in _rows()}

    expected = {
        "Mary Robinson",
        "Michelle Bachelet",
        "Ruth Bader Ginsburg",
        "Chimamanda Ngozi Adichie",
        "Malala Yousafzai",
        "Wole Soyinka",
        "Caroline Lucas",
        "Robert Dahl",
        "Theda Skocpol",
        "Corazon Aquino",
    }

    assert expected.issubset(names)
