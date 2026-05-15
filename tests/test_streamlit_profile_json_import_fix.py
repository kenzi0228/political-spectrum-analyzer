from pathlib import Path


def test_streamlit_profile_import_controls_exist_before_input_widgets():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "def _render_profile_import_controls" in content
    assert "_render_profile_import_controls(profile_index)" in content
    assert "upload_nonce" in content
    assert "st.rerun()" in content


def test_streamlit_profile_import_no_longer_modifies_widget_after_instantiation_pattern():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    import_call_index = content.index("_render_profile_import_controls(profile_index)")
    name_widget_index = content.index("profile_name = st.text_input")

    assert import_call_index < name_widget_index


def test_streamlit_profile_import_releases_uploaded_file_after_load():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "st.session_state[f\"{prefix}_upload_nonce\"] += 1" in content
    assert "Profile loaded. The fields have been filled and remain editable." in content


def test_streamlit_profile_download_is_separate_from_import():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "Import a saved profile" in content
    assert "Save this profile" in content
    assert "Download this profile JSON" in content