from pathlib import Path
import re


APP = Path("streamlit_app.py")
DOC = Path("docs/real_streamlit_ui_integration.md")
README = Path("README.md")


def _main_block() -> str:
    content = APP.read_text(encoding="utf-8")
    match = re.search(r"def main\(\) -> None:(.*?)(?:\n\nif __name__|\Z)", content, flags=re.S)
    assert match is not None
    return match.group(1)


def test_main_uses_active_multiselect_reference_filters():
    main = _main_block()

    assert "_render_reference_multiselect_filters(personalities, language)" in main
    assert "_render_reference_filters(personalities)" not in main


def test_active_reference_filters_include_gender_and_confidence():
    content = APP.read_text(encoding="utf-8")

    function_start = content.index("def _render_reference_multiselect_filters")
    function_end = content.index("def _render_advanced_profile_comparisons", function_start)
    function_body = content[function_start:function_end]

    assert '"gender"' in function_body
    assert '"confidence"' in function_body
    assert "st.sidebar.multiselect" in function_body
    assert "active_reference_filter_gender" in function_body


def test_main_uses_integrated_analysis_v3_not_legacy_analysis():
    main = _main_block()

    assert "_render_integrated_analysis_v3(people, filtered_personalities, language)" in main
    assert "_render_analysis(people, personalities)" not in main


def test_score_input_mode_label_is_visible_before_sidebar_options():
    main = _main_block()

    assert "Score input mode" in main
    assert "slider-based manual scoring" in main


def test_reference_dataset_tab_uses_filtered_personalities():
    main = _main_block()

    assert "for person in filtered_personalities" in main


def test_real_ui_integration_doc_exists():
    assert DOC.exists()

    content = DOC.read_text(encoding="utf-8")
    assert "Real Streamlit UI integration" in content
    assert "not only defined as helpers" in content
    assert "gender" in content.lower()


def test_readme_mentions_real_streamlit_ui_integration():
    content = README.read_text(encoding="utf-8")

    assert "Real Streamlit UI integration" in content
