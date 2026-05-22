from pathlib import Path


APP = Path("streamlit_app.py")
TEXT = Path("src/political_spectrum_analyzer/streamlit_ui/text.py")
METHODOLOGY = Path("src/political_spectrum_analyzer/streamlit_ui/methodology.py")


def test_streamlit_app_contains_personalized_profile_reading():
    app_content = APP.read_text(encoding="utf-8")
    content = Path("src/political_spectrum_analyzer/streamlit_ui/analysis_rendering.py").read_text(encoding="utf-8")
    text_content = TEXT.read_text(encoding="utf-8")

    assert "_render_analysis" in app_content
    assert "render_profile_interpretation" in content
    assert "analysis_personalized_reading" in content
    assert "Personalized profile reading" in text_content
    assert "Dominant axes" in text_content
    assert "Weakest axes" in text_content
    assert "Axis-by-axis balance" in text_content
    assert "Score-by-score reading" in text_content


def test_streamlit_methodology_is_product_oriented():
    content = (
        APP.read_text(encoding="utf-8")
        + TEXT.read_text(encoding="utf-8")
        + METHODOLOGY.read_text(encoding="utf-8")
    ).lower()

    assert "how the analyzer works" in content
    assert "score blocks and coefficients" in content
    assert "raw axis calculation" in content
    assert "secondary adjustments" in content
    assert "normalization and final coordinates" in content
    assert "limitations" not in content


def test_streamlit_has_product_facing_profile_interpretation():
    content = (
        Path("src/political_spectrum_analyzer/streamlit_ui/analysis_rendering.py").read_text(encoding="utf-8")
        + TEXT.read_text(encoding="utf-8")
    ).lower()

    assert "personalized profile reading" in content
    assert "dominant axes" in content
    assert "weakest axes" in content
    assert "axis-by-axis balance" in content
    assert "score-by-score reading" in content
    assert "limitations" not in content
