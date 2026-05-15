from pathlib import Path


def test_streamlit_app_contains_personalized_profile_reading():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "_render_profile_interpretation" in content
    assert "Personalized profile reading" in content
    assert "Dominant axes" in content
    assert "Weakest axes" in content
    assert "Axis-by-axis balance" in content


def test_streamlit_methodology_is_product_oriented():
    content = Path("streamlit_app.py").read_text(encoding="utf-8").lower()

    assert "how the analyzer works" in content
    assert "calculation formula" in content
    assert "meaning of the 16 axes" in content
    assert "limitations" not in content

def test_streamlit_has_product_facing_profile_interpretation():
    content = Path("streamlit_app.py").read_text(encoding="utf-8").lower()

    assert "personalized profile reading" in content
    assert "dominant axes" in content
    assert "weakest axes" in content
    assert "axis-by-axis balance" in content
    assert "limitations" not in content
