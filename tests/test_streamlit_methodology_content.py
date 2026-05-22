from pathlib import Path


APP = Path("streamlit_app.py")
TEXT = Path("src/political_spectrum_analyzer/streamlit_ui/text.py")
METHODOLOGY = Path("src/political_spectrum_analyzer/streamlit_ui/methodology.py")


def test_streamlit_methodology_tab_explains_formula_and_axes():
    content = APP.read_text(encoding="utf-8").lower()

    assert "def _render_methodology_tab" in content
    assert "left_economic" in content
    assert "right_economic" in content
    assert "libertarian_social" in content
    assert "authoritarian_social" in content
    assert "economic_raw = right_economic - left_economic" in content
    assert "societal_raw = authoritarian_social - libertarian_social" in content


def test_streamlit_methodology_tab_mentions_all_16_axes():
    content = (APP.read_text(encoding="utf-8") + TEXT.read_text(encoding="utf-8")).lower()

    expected_axes = [
        "constructivisme",
        "essentialisme",
        "justice_rehabilitative",
        "justice_punitive",
        "progressisme",
        "conservatisme",
        "internationalisme",
        "nationalisme",
        "communisme",
        "capitalisme",
        "regulation",
        "laissez_faire",
        "ecologie",
        "productivisme",
        "revolution",
        "reformisme",
    ]

    for axis in expected_axes:
        assert axis in content


def test_streamlit_methodology_is_product_facing_not_academic():
    content = (
        APP.read_text(encoding="utf-8")
        + TEXT.read_text(encoding="utf-8")
        + METHODOLOGY.read_text(encoding="utf-8")
    ).lower()

    assert "how the analyzer works" in content
    assert "how to read your result" in content
    assert "personalized profile reading" in content
    assert "next planned improvement" not in content
    assert "limitations" not in content
