import csv
from pathlib import Path


PERSONALITIES = Path("data/reference/personalities.csv")
SUMMARY = Path("data/reference/reference_dataset_summary.csv")
GENDER_ROLE_SUMMARY = Path("data/reference/reference_dataset_gender_role_summary.csv")
REPORT = Path("docs/reference_dataset_quality_report.md")
GENDER_DOC = Path("docs/gender_metadata.md")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _summary() -> dict[str, str]:
    return {row["metric"]: row["value"] for row in _rows(SUMMARY)}


def test_gender_metadata_document_exists():
    assert GENDER_DOC.exists()


def test_gender_role_summary_exists():
    assert GENDER_ROLE_SUMMARY.exists()


def test_gender_role_summary_contains_expected_columns():
    rows = _rows(GENDER_ROLE_SUMMARY)

    assert rows
    assert {
        "role_category",
        "total",
        "male",
        "female",
        "unknown",
        "female_share_percent",
    }.issubset(rows[0])


def test_reference_summary_contains_gender_metrics():
    summary = _summary()

    assert "male_count" in summary
    assert "female_count" in summary
    assert "unknown_gender_count" in summary
    assert "female_share_percent" in summary


def test_gender_counts_match_dataset():
    dataset_rows = _rows(PERSONALITIES)
    summary = _summary()

    male = sum(1 for row in dataset_rows if row["gender"] == "male")
    female = sum(1 for row in dataset_rows if row["gender"] == "female")
    unknown = sum(1 for row in dataset_rows if row["gender"] == "unknown")

    assert int(summary["male_count"]) == male
    assert int(summary["female_count"]) == female
    assert int(summary["unknown_gender_count"]) == unknown


def test_quality_report_mentions_gender_distribution():
    content = REPORT.read_text(encoding="utf-8")

    assert "Gender distribution" in content
    assert "Gender by role category" in content
    assert "metadata only" in content
