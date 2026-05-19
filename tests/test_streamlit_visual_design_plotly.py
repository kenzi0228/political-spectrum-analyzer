from pathlib import Path


APP = Path("streamlit_app.py")
CONFIG = Path(".streamlit/config.toml")
DOC = Path("docs/streamlit_visual_design.md")
REQ = Path("requirements.txt")


def test_streamlit_theme_config_exists():
    assert CONFIG.exists()


def test_streamlit_theme_config_uses_professional_dark_theme():
    content = CONFIG.read_text(encoding="utf-8")

    assert '[theme]' in content
    assert 'primaryColor = "#6C63FF"' in content
    assert 'backgroundColor = "#0E1117"' in content
    assert 'secondaryBackgroundColor = "#1A1D2E"' in content
    assert 'textColor = "#FAFAFA"' in content


def test_streamlit_app_contains_custom_css_layer():
    content = APP.read_text(encoding="utf-8")

    assert "STREAMLIT_THEME_CSS" in content
    assert "apply_professional_streamlit_theme" in content
    assert "psa-hero" in content


def test_streamlit_app_contains_plotly_reference_helper():
    content = APP.read_text(encoding="utf-8")

    assert "build_reference_plotly_figure" in content
    assert "render_reference_plotly_chart" in content
    assert "st.plotly_chart" in content
    assert "PLOTLY_REFERENCE_TOOLTIP_FIELDS" in content


def test_plotly_dependency_is_declared_when_requirements_file_exists():
    if not REQ.exists():
        return

    content = REQ.read_text(encoding="utf-8").lower()
    assert "plotly" in content


def test_visual_design_doc_exists():
    assert DOC.exists()
    content = DOC.read_text(encoding="utf-8")

    assert "Streamlit visual design" in content
    assert "Plotly" in content
    assert "Compatibility rule" in content
