from pathlib import Path

from political_spectrum_analyzer.domain.models import PersonResult, PersonalityPoint
from political_spectrum_analyzer.services.export_results_service import (
    build_export_rows,
    export_analysis_to_csv,
)


def _sample_person():
    return PersonResult(
        name="Test profile",
        scores={},
        x=-1.0,
        y=0.5,
    )


def _sample_references():
    return [
        PersonalityPoint(
            name="Close reference",
            display_group="Test",
            x=-1.1,
            y=0.6,
        ),
        PersonalityPoint(
            name="Far reference",
            display_group="Test",
            x=3.0,
            y=3.0,
        ),
    ]


def test_build_export_rows_profiles_only():
    rows = build_export_rows(
        people=[_sample_person()],
        personalities=_sample_references(),
        mode="profiles_only",
    )

    assert len(rows) == 1
    assert rows[0]["record_type"] == "profile"
    assert rows[0]["profile_name"] == "Test profile"


def test_build_export_rows_with_closest_references():
    rows = build_export_rows(
        people=[_sample_person()],
        personalities=_sample_references(),
        mode="closest_references",
        closest_count=1,
    )

    assert len(rows) == 2
    assert rows[0]["record_type"] == "profile"
    assert rows[1]["record_type"] == "reference"
    assert rows[1]["reference_name"] == "Close reference"


def test_build_export_rows_with_all_references():
    rows = build_export_rows(
        people=[_sample_person()],
        personalities=_sample_references(),
        mode="all_references",
    )

    assert len(rows) == 3
    assert rows[1]["reference_name"] == "Close reference"
    assert rows[2]["reference_name"] == "Far reference"


def test_export_analysis_to_csv_creates_file(tmp_path: Path):
    output_path = tmp_path / "analysis_export.csv"

    export_analysis_to_csv(
        file_path=output_path,
        people=[_sample_person()],
        personalities=_sample_references(),
        mode="closest_references",
        closest_count=1,
    )

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8-sig")
    assert "Test profile" in content
    assert "Close reference" in content