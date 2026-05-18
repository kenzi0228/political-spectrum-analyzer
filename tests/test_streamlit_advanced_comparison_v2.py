from pathlib import Path


def test_streamlit_imports_advanced_comparison_service():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "advanced_profile_comparison_service" in content
    assert "build_advanced_profile_comparisons" in content
    assert "build_similarity_matrix" in content


def test_streamlit_defines_advanced_comparison_renderer():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "def _render_advanced_profile_comparisons" in content
    assert "advanced_comparison_header" in content
    assert "_render_advanced_profile_comparisons(people_results, language)" in content


def test_readme_documents_advanced_comparison_v2():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Advanced comparison v2" in content
    assert "economic similarity" in content
    assert "secondary-dimension similarity" in content
    assert "similarity matrix" in content
