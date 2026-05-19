from pathlib import Path


def test_homepage_does_not_show_technology_tags():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "feature-pill" in content
    assert "Python</span>" not in content
    assert "Streamlit</span>" not in content
    assert "Plotly</span>" not in content
    assert "500 reference profiles</span>" not in content


def test_manual_numeric_entry_is_default():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "Manual numeric entry" in content
    assert "value=True" in content
    assert "On: type exact values" in content


def test_methodology_explains_coefficients_explicitly():
    content = Path("streamlit_app.py").read_text(encoding="utf-8").lower()

    assert "score blocks and coefficients" in content
    assert "economic-left block" in content
    assert "economic-right block" in content
    assert "secondary adjustments" in content
    assert "normalization and final coordinates" in content
    assert "0.90 * communisme" in content
    assert "0.90 * capitalisme" in content