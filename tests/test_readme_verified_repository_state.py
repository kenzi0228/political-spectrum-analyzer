from pathlib import Path
import csv


README = Path("README.md")
PERSONALITIES = Path("data/reference/personalities.csv")


def _readme() -> str:
    return README.read_text(encoding="utf-8")


def _dataset_count() -> int:
    with PERSONALITIES.open("r", encoding="utf-8-sig", newline="") as file:
        return len(list(csv.DictReader(file)))


def test_readme_mentions_actual_reference_dataset_size():
    assert f"**{_dataset_count()} profiles**" in _readme()


def test_readme_documents_current_scoring_model_v3_and_frames_legacy_v2():
    text = _readme()

    assert "0.95 * communisme" in text
    assert "0.80 * laissez_faire" in text
    assert "0.38 * ecologie" in text
    assert "tanh(0.015 * economic_raw)" in text
    assert "Legacy scoring model v2 anchor" in text
    assert "This block is retained only as a legacy documentation contract" in text

    assert "0.25 * revolution" not in text
    assert "0.20 * reformisme" not in text
    assert "raw / 120" not in text


def test_readme_frames_demo_placeholder_as_template_not_fake_claim():
    text = _readme()

    assert "https://example.com" not in text
    assert "TODO" not in text
    assert "coming soon" not in text.lower()
    assert "Deployment template anchor" in text
    assert "This placeholder is kept for forks and deployment documentation tests" in text


def test_readme_points_to_existing_core_paths():
    text = _readme()

    for path in ["streamlit_app.py", "data/reference/personalities.csv", "tests"]:
        assert path in text
        assert Path(path).exists()


def test_readme_license_section_exists():
    assert "## License" in _readme()
