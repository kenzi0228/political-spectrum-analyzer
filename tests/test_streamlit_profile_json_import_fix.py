from pathlib import Path


PROFILE_INPUTS = Path("src/political_spectrum_analyzer/streamlit_ui/profile_inputs.py")
TEXT = Path("src/political_spectrum_analyzer/streamlit_ui/text.py")


def test_streamlit_profile_import_controls_exist_before_input_widgets():
    content = PROFILE_INPUTS.read_text(encoding="utf-8")

    assert "def render_profile_import_controls" in content
    assert "render_profile_import_controls(profile_index, translate)" in content
    assert "upload_nonce" in content
    assert "st.rerun()" in content


def test_streamlit_profile_import_no_longer_modifies_widget_after_instantiation_pattern():
    content = PROFILE_INPUTS.read_text(encoding="utf-8")

    import_call_index = content.index("render_profile_import_controls(profile_index, translate)")
    name_widget_index = content.index("profile_name = st.text_input")

    assert import_call_index < name_widget_index


def test_streamlit_profile_import_releases_uploaded_file_after_load():
    content = PROFILE_INPUTS.read_text(encoding="utf-8")

    assert "st.session_state[f\"{prefix}_upload_nonce\"] += 1" in content
    assert "profile_loaded" in content or "Profile loaded. The fields have been filled and remain editable." in content


def test_streamlit_profile_download_is_separate_from_import():
    content = TEXT.read_text(encoding="utf-8")
    input_content = PROFILE_INPUTS.read_text(encoding="utf-8")

    assert "import_saved_profile" in content or "Import a saved profile" in content
    assert "save_this_profile" in content or "Save this profile" in content
    assert "download_profile_json" in content or "Download this profile JSON" in content
    assert "render_profile_import_export" in input_content
