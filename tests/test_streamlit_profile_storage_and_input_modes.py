from pathlib import Path


APP = Path("streamlit_app.py")
PROFILE_INPUTS = Path("src/political_spectrum_analyzer/streamlit_ui/profile_inputs.py")
TEXT = Path("src/political_spectrum_analyzer/streamlit_ui/text.py")


def test_streamlit_app_has_no_mojibake_symbols():
    content = APP.read_text(encoding="utf-8")

    forbidden_fragments = ["Ãƒ", "Ã¢", "â‚¬", "â„¢"]

    for fragment in forbidden_fragments:
        assert fragment not in content


def test_streamlit_app_has_manual_numeric_entry_toggle():
    app_content = APP.read_text(encoding="utf-8") + TEXT.read_text(encoding="utf-8")
    input_content = PROFILE_INPUTS.read_text(encoding="utf-8")

    assert "manual_numeric_entry" in app_content or "Manual numeric entry" in app_content
    assert "value=True" in app_content
    assert "st.number_input" in input_content
    assert "st.slider" in input_content


def test_streamlit_app_has_separated_profile_import_and_save():
    app_content = APP.read_text(encoding="utf-8") + TEXT.read_text(encoding="utf-8")
    input_content = PROFILE_INPUTS.read_text(encoding="utf-8")

    assert "import_saved_profile" in app_content or "Import a saved profile" in app_content
    assert "select_saved_json" in app_content or "Select a saved profile JSON" in app_content
    assert "load_this_profile" in app_content or "Load this profile" in app_content
    assert "save_this_profile" in app_content or "Save this profile" in app_content
    assert "download_profile_json" in app_content or "Download this profile JSON" in app_content
    assert "political_spectrum_profile.v1" in input_content


def test_streamlit_mentions_future_authenticated_storage():
    content = APP.read_text(encoding="utf-8") + TEXT.read_text(encoding="utf-8")

    assert "future authenticated version" in content or "future version authentifiee" in content
