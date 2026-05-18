import csv
from pathlib import Path


SUMMARY = Path("data/reference/reference_dataset_summary.csv")
REPORT = Path("docs/reference_dataset_quality_report.md")
PERSONALITIES = Path("data/reference/personalities.csv")


def _summary() -> dict[str, str]:
    with SUMMARY.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row["metric"]: row["value"] for row in csv.DictReader(handle)}


def _profile_count() -> int:
    with PERSONALITIES.open("r", encoding="utf-8-sig", newline="") as handle:
        return len(list(csv.DictReader(handle)))


def test_reference_dataset_summary_file_exists():
    assert SUMMARY.exists()


def test_reference_dataset_quality_report_exists():
    assert REPORT.exists()


def test_reference_dataset_summary_matches_dataset_size():
    summary = _summary()

    assert int(summary["profile_count"]) == _profile_count()


def test_reference_dataset_summary_tracks_core_metrics():
    summary = _summary()

    expected = {
        "profile_count",
        "ideology_family_count",
        "taxonomy_family_count",
        "missing_taxonomy_family_count",
        "role_category_count",
        "country_code_count",
        "average_ux",
        "average_uy",
        "left_libertarian_count",
        "right_authoritarian_count",
    }

    assert expected.issubset(summary)


def test_reference_dataset_report_documents_quality_gates():
    content = REPORT.read_text(encoding="utf-8")

    assert "Quality gates" in content
    assert "Ideology family distribution" in content
    assert "Country-code coverage" in content
    assert "Confidence distribution" in content
