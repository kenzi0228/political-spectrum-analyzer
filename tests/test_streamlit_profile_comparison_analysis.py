from pathlib import Path


ADVANCED_RENDERING = Path("src/political_spectrum_analyzer/streamlit_ui/advanced_rendering.py")


def test_streamlit_imports_profile_comparison_service():
    content = ADVANCED_RENDERING.read_text(encoding="utf-8")

    assert "profile_comparison_service" in content
    assert "build_profile_comparisons" in content
    assert "build_comparison_rows" in content


def test_streamlit_defines_profile_comparison_renderer():
    app_content = Path("streamlit_app.py").read_text(encoding="utf-8")
    content = ADVANCED_RENDERING.read_text(encoding="utf-8")

    assert "def render_profile_comparison_analysis" in content
    assert "render_profile_comparison_analysis as _render_profile_comparison_analysis" in app_content
    assert "profile_comparison_header" in content
    assert "ideological_similarity_score" in Path(
        "src/political_spectrum_analyzer/services/profile_comparison_service.py"
    ).read_text(encoding="utf-8")


def test_readme_mentions_profile_comparison_analysis():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Profile comparison analysis" in content
    assert "ideological similarity score" in content
    assert "largest score gaps" in content
