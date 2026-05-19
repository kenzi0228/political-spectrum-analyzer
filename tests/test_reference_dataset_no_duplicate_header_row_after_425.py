import csv
from pathlib import Path


PERSONALITIES = Path("data/reference/personalities.csv")


def test_no_duplicate_csv_header_row_after_425_expansion():
    with PERSONALITIES.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        assert row["name"].lower() != "name"
        assert row["x"].lower() != "x"
        assert row["ux"].lower() != "ux"
        assert row["confidence"].lower() != "confidence"
        assert row["is_estimated"].lower() != "is_estimated"
