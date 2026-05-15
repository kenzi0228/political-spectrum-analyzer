from pathlib import Path


def test_streamlit_app_has_no_mojibake_symbols():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    forbidden_fragments = ["Ãƒ", "Ã¢", "â‚¬", "â„¢"]

    for fragment in forbidden_fragments:
        assert fragment not in content


def test_streamlit_app_has_manual_numeric_entry_toggle():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "manual_numeric_entry" in content or "Manual numeric entry" in content
    assert "value=True" in content
    assert "st.number_input" in content
    assert "st.slider" in content


def test_streamlit_app_has_separated_profile_import_and_save():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "import_saved_profile" in content or "Import a saved profile" in content
    assert "select_saved_json" in content or "Select a saved profile JSON" in content
    assert "load_this_profile" in content or "Load this profile" in content
    assert "save_this_profile" in content or "Save this profile" in content
    assert "download_profile_json" in content or "Download this profile JSON" in content
    assert "political_spectrum_profile.v1" in content


def test_streamlit_mentions_future_authenticated_storage():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "future authenticated version" in content or "future version authentifiee" in content