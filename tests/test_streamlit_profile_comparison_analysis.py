from pathlib import Path


def test_streamlit_imports_profile_comparison_service():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "profile_comparison_service" in content
    assert "build_profile_comparisons" in content
    assert "build_comparison_rows" in content


def test_streamlit_defines_profile_comparison_renderer():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "def _render_profile_comparison_analysis" in content
    assert "Profile comparison analysis" in content
    assert "ideological_similarity_score" in Path(
        "src/political_spectrum_analyzer/services/profile_comparison_service.py"
    ).read_text(encoding="utf-8")


def test_readme_mentions_profile_comparison_analysis():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Profile comparison analysis" in content
    assert "ideological similarity score" in content
    assert "largest score gaps" in content