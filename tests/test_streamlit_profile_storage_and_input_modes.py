from pathlib import Path


def test_streamlit_app_has_no_mojibake_symbols():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    forbidden_fragments = ["Ãƒ", "Ã¢", "â‚¬", "â„¢"]

    for fragment in forbidden_fragments:
        assert fragment not in content


def test_streamlit_app_has_precise_score_entry_toggle():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "Precise score entry" in content
    assert "st.number_input" in content
    assert "st.slider" in content


def test_streamlit_app_has_profile_save_and_import():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "Save or import this profile" in content
    assert "Download this profile JSON" in content
    assert "Load saved profile into this form" in content
    assert "political_spectrum_profile.v1" in content


def test_streamlit_mentions_future_authenticated_storage():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "future authenticated version" in content