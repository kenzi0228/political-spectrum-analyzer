from pathlib import Path

from political_spectrum_analyzer.streamlit_ui.text import UI_TEXT


APP = Path("streamlit_app.py")
CONTENT_PAGES = Path("src/political_spectrum_analyzer/streamlit_ui/content_pages.py")
TEXT = Path("src/political_spectrum_analyzer/streamlit_ui/text.py")
METHODOLOGY = Path("src/political_spectrum_analyzer/streamlit_ui/methodology.py")


def test_ui_text_does_not_call_translation_function_inside_dictionary():
    content = TEXT.read_text(encoding="utf-8")
    ui_start = content.index("UI_TEXT: dict")
    t_start = content.index("def translate", ui_start)
    ui_block = content[ui_start:t_start]
    assert "translate(" not in ui_block


def test_recommended_workflow_markdown_uses_helper():
    app_content = APP.read_text(encoding="utf-8")
    page_content = CONTENT_PAGES.read_text(encoding="utf-8")
    text_content = TEXT.read_text(encoding="utf-8")

    assert "markdown_text as _md_text" in app_content
    assert "st.markdown(markdown_text(language, \"recommended_workflow_body\"))" in page_content
    assert "1. Gardez la saisie numerique activee" not in text_content
    assert "2. Saisissez d'abord un profil" not in text_content
    assert "- Gardez la saisie numerique activee" in text_content


def test_methodology_explains_coefficients_in_both_languages():
    content = (
        APP.read_text(encoding="utf-8")
        + TEXT.read_text(encoding="utf-8")
        + METHODOLOGY.read_text(encoding="utf-8")
    )

    assert "A coefficient is a weight" in content
    assert "Un coefficient est un poids" in content
    assert "0.90 * communisme" in content
    assert "0.70 * regulation" in content
    assert "0.12 * (productivisme - ecologie)" in content


def test_streamlit_translation_covers_profile_import_and_input_labels():
    content = TEXT.read_text(encoding="utf-8")

    assert "profile_count_label" in content
    assert "import_saved_profile" in content
    assert "download_profile_json" in content
    assert "copied_text_import" in content


def test_streamlit_translation_keys_are_complete_for_english_and_french():
    assert set(UI_TEXT["en"]) == set(UI_TEXT["fr"])

    required_runtime_keys = {
        "active_tab_label",
        "inactive_tab_notice",
        "score_input_mode_caption",
        "reference_dataset_not_loaded",
        "filter_role_categories",
        "analysis_score_by_score",
        "download_analysis_csv",
    }

    for key in required_runtime_keys:
        assert UI_TEXT["en"][key]
        assert UI_TEXT["fr"][key]


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
