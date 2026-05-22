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


def test_readme_documents_current_scoring_model_v2():
    text = _readme()

    assert "The current coordinate methodology is scoring model v2." in text
    assert "0.90 * communisme" in text
    assert "0.75 * laissez_faire" in text
    assert "0.35 * ecologie" in text
    assert "0.25 * productivisme" in text
    assert "0.50 * internationalisme" in text
    assert "0.60 * essentialisme" in text
    assert "0.70 * justice_punitive" in text
    assert "0.70 * conservatisme" in text
    assert "0.50 * nationalisme" in text
    assert "0.12 * (productivisme - ecologie)" in text
    assert "0.10 * (nationalisme - internationalisme)" in text
    assert "0.08 * (revolution - reformisme)" in text
    assert "economic_normalized = economic_raw / 120" in text
    assert "sigmoid_scaled" in text
    assert "Legacy scoring model v3 anchor" in text
    assert "This block is retained only as a legacy documentation contract" in text


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
