import csv
from pathlib import Path


PERSONALITIES = Path("data/reference/personalities.csv")


def _country_tokens(value: str) -> set[str]:
    return {
        token.strip().lower()
        for token in str(value or "").replace(",", ";").split(";")
        if token.strip()
    }


def test_reference_dataset_has_no_israel_country_token_after_250_expansion():
    with PERSONALITIES.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    offenders = [
        row["name"]
        for row in rows
        if "israel" in _country_tokens(row.get("country", ""))
    ]

    assert offenders == []
