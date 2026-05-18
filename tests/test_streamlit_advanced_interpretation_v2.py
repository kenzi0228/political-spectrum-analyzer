from pathlib import Path


def test_streamlit_imports_advanced_interpretation_service():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "advanced_profile_interpretation_service" in content
    assert "build_advanced_profile_interpretation" in content
    assert "build_advanced_interpretation_rows" in content


def test_streamlit_defines_advanced_interpretation_renderer():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "def _render_advanced_profile_interpretations" in content
    assert "advanced_interpretation_header" in content
    assert "_render_advanced_profile_interpretations(people_results, language)" in content


def test_readme_documents_advanced_interpretation_v2():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Advanced interpretation v2" in content
    assert "coherence score" in content
    assert "radicality score" in content
    assert "secondary dimensions" in content
