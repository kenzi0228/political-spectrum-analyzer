from pathlib import Path


ADVANCED_RENDERING = Path("src/political_spectrum_analyzer/streamlit_ui/advanced_rendering.py")


def test_streamlit_imports_advanced_comparison_service():
    content = ADVANCED_RENDERING.read_text(encoding="utf-8")

    assert "advanced_profile_comparison_service" in content
    assert "build_advanced_profile_comparisons" in content
    assert "build_similarity_matrix" in content


def test_streamlit_defines_advanced_comparison_renderer():
    app_content = Path("streamlit_app.py").read_text(encoding="utf-8")
    content = ADVANCED_RENDERING.read_text(encoding="utf-8")

    assert "def render_advanced_profile_comparisons" in content
    assert "render_advanced_profile_comparisons as _render_advanced_profile_comparisons" in app_content
    assert "advanced_comparison_header" in content
    assert "_render_advanced_profile_comparisons(people_results, language, _t)" in app_content


def test_readme_documents_advanced_comparison_v2():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Advanced comparison v2" in content
    assert "economic similarity" in content
    assert "secondary-dimension similarity" in content
    assert "similarity matrix" in content
