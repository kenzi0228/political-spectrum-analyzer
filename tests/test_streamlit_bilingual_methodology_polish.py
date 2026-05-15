from pathlib import Path


def test_ui_text_does_not_call_translation_function_inside_dictionary():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")
    ui_start = content.index("UI_TEXT: dict")
    t_start = content.index("def _t", ui_start)
    ui_block = content[ui_start:t_start]
    assert "_t(" not in ui_block


def test_recommended_workflow_markdown_uses_helper():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "def _md_text" in content
    assert "st.markdown(_md_text(language, \"recommended_workflow_body\"))" in content
    assert "1. Gardez la saisie numerique activee" not in content
    assert "2. Saisissez d'abord un profil" not in content
    assert "- Gardez la saisie numerique activee" in content


def test_methodology_explains_coefficients_in_both_languages():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "A coefficient is a weight" in content
    assert "Un coefficient est un poids" in content
    assert "0.90 * communisme" in content
    assert "0.75 * regulation" in content
    assert "0.12 * (productivisme - ecologie)" in content


def test_streamlit_translation_covers_profile_import_and_input_labels():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "profile_count_label" in content
    assert "import_saved_profile" in content
    assert "download_profile_json" in content
    assert "copied_text_import" in content


def test_assets_folder_documentation_exists():
    assert Path("docs/assets/.gitkeep").exists()
    assert Path("docs/assets/README.md").exists()

    content = Path("docs/assets/README.md").read_text(encoding="utf-8")

    assert "streamlit-home.png" in content
    assert "streamlit-profile-analysis.png" in content


def test_readme_mentions_screenshots_to_add():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Screenshots to add" in content
    assert "docs/assets/" in content
