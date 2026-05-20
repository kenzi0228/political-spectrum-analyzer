from pathlib import Path


APP = Path("streamlit_app.py")


def test_profile_reading_does_not_duplicate_synthesis_in_three_cards():
    content = APP.read_text(encoding="utf-8")
    assert "reading_col1.info(interpretation.economic_reading)" not in content
    assert "reading_col2.info(interpretation.societal_reading)" not in content
    assert "reading_col3.info(interpretation.strategic_reading)" not in content


def test_reference_filter_aliases_and_real_value_fallbacks_exist():
    content = APP.read_text(encoding="utf-8")
    assert "REFERENCE_FILTER_FIELD_ALIASES" in content
    assert "role_category" in content
    assert "display_group" in content
    assert "_reference_metadata_lookup_by_name" in content
    assert "_reference_multiselect_options(reference_items, field_name)" in content


def test_country_code_filter_label_is_renamed():
    content = APP.read_text(encoding="utf-8")
    assert '"Country code filter"' in content


def test_original_detailed_analysis_is_runtime_path():
    content = APP.read_text(encoding="utf-8")
    main_start = content.index("def main")
    entrypoint = content.rfind('if __name__ == "__main__"')
    main_body = content[main_start:entrypoint]
    assert "_render_analysis(people, filtered_personalities)" in main_body
    assert "_render_integrated_analysis_v3(people, filtered_personalities, language)" not in main_body
