from pathlib import Path


APP = Path("streamlit_app.py")
DOC = Path("docs/streamlit_ui_review_fixes.md")


def test_theme_mode_selector_exists():
    content = APP.read_text(encoding="utf-8")
    assert "render_theme_mode_selector" in content
    assert "Interface theme" in content
    assert "Light" in content
    assert "Dark" in content


def test_sidebar_css_is_mode_aware():
    content = APP.read_text(encoding="utf-8")
    assert '[data-testid="stSidebar"]' in content
    assert "_theme_palette" in content
    assert "sidebar_bg" in content


def test_gender_filter_exists_for_reference_profiles():
    content = APP.read_text(encoding="utf-8")
    assert "Gender filter" in content
    assert "render_gender_filter_selector" in content
    assert "filter_reference_dataframe_by_gender" in content
    assert "filter_reference_rows_by_gender" in content


def test_profile_reading_deduplication_helper_exists():
    content = APP.read_text(encoding="utf-8")
    assert "deduplicate_profile_reading_sentences" in content
    assert "Remove repeated sentences" in content


def test_score_input_mode_has_explicit_label_and_help():
    content = APP.read_text(encoding="utf-8")
    assert "SCORE_INPUT_MODE_LABEL" in content
    assert "Score input mode" in content
    assert "SCORE_INPUT_MODE_HELP" in content


def test_ui_review_doc_exists():
    assert DOC.exists()
    content = DOC.read_text(encoding="utf-8")
    assert "Streamlit UI review fixes" in content
    assert "Gender is metadata only" in content
