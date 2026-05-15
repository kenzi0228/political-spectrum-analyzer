from pathlib import Path


def test_streamlit_methodology_tab_explains_formula_and_axes():
    content = Path("streamlit_app.py").read_text(encoding="utf-8").lower()

    assert "def _render_methodology_tab" in content
    assert "left_economic" in content
    assert "right_economic" in content
    assert "libertarian_social" in content
    assert "authoritarian_social" in content
    assert "economic_raw = right_economic - left_economic" in content
    assert "societal_raw = authoritarian_social - libertarian_social" in content


def test_streamlit_methodology_tab_mentions_all_16_axes():
    content = Path("streamlit_app.py").read_text(encoding="utf-8").lower()

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


def test_streamlit_methodology_tab_announces_next_profile_analysis_step():
    content = Path("streamlit_app.py").read_text(encoding="utf-8").lower()

    assert "next planned improvement" in content
    assert "detailed profile analysis" in content