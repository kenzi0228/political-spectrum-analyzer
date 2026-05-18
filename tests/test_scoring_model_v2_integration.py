from pathlib import Path


def test_scoring_model_v2_module_exists():
    content = Path("src/political_spectrum_analyzer/model/scoring_model_v2.py").read_text(encoding="utf-8")

    assert "compute_position" in content
    assert "compute_projection_breakdown" in content
    assert "compute_secondary_dimensions" in content
    assert "tanh" in content


def test_transforms_exposes_scoring_model_v2_wrappers():
    content = Path("src/political_spectrum_analyzer/model/transforms.py").read_text(encoding="utf-8")

    assert "compute_position_from_scores_v2" in content
    assert "compute_projection_breakdown_v2" in content
    assert "compute_secondary_dimensions_v2" in content


def test_readme_documents_scoring_model_v2():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Scoring model v2" in content
    assert "revolution" in content
    assert "reformisme" in content
    assert "tanh" in content


def test_methodology_documents_scoring_model_v2_when_present():
    path = Path("docs/methodology.md")

    if not path.exists():
        return

    content = path.read_text(encoding="utf-8")

    assert "Scoring model v2" in content
    assert "revolution" in content
    assert "tanh" in content
