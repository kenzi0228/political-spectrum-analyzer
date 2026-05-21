from pathlib import Path


APP = Path("streamlit_app.py")


def test_sidebar_is_forced_dark_for_readability():
    content = APP.read_text(encoding="utf-8")

    assert "FORCE_DARK_SIDEBAR_CSS" in content
    assert "#0E1117" in content
    assert "#111522" in content
    assert "_force_dark_sidebar()" in content


def test_filters_include_any_none_and_real_value_pipeline():
    content = APP.read_text(encoding="utf-8")
    start = content.index("def _render_reference_multiselect_filters")
    end = content.index("def _render_advanced_profile_comparisons", start)
    body = content[start:end]

    assert '"Any"' in body
    assert '"None"' in body
    assert "default=[]" in body
    assert "has_filter_selection = any(selected_filters.values())" in body
    assert "_reference_multiselect_options(reference_items, field_name)" in body
    assert "cleaned_values" in body
    assert "reference profiles displayed" in body
    assert "reference profiles match the current filters" in body


def test_main_uses_original_detailed_analysis_renderer():
    content = APP.read_text(encoding="utf-8")
    main_start = content.index("def main")
    entrypoint = content.rfind('if __name__ == "__main__"')
    main_body = content[main_start:entrypoint]

    assert "_render_analysis(people, filtered_personalities)" in main_body
    assert "_render_integrated_analysis_v3(people, filtered_personalities, language)" not in main_body


def test_reference_dataset_is_loaded_only_for_reference_views():
    content = APP.read_text(encoding="utf-8")
    main_start = content.index("def main")
    entrypoint = content.rfind('if __name__ == "__main__"')
    main_body = content[main_start:entrypoint]

    active_view_pos = main_body.index("active_view = _render_active_view_selector(language)")
    load_pos = main_body.index("personalities = _load_reference_personalities()")

    assert active_view_pos < load_pos
    assert "if _view_requires_reference_dataset(active_view):" in main_body
    assert 'return active_view in {"visualization", "reference"}' in content
    assert "Reference dataset is not loaded on this tab." in main_body


def test_people_can_be_rebuilt_from_session_state_without_rendering_inputs():
    content = APP.read_text(encoding="utf-8")

    assert "def _build_people_from_state()" in content
    assert "people = _build_people_from_state()" in content
    assert 'key="profile_count"' in content


def test_advanced_helpers_are_defined_before_entrypoint():
    content = APP.read_text(encoding="utf-8")
    entrypoint = content.rfind('if __name__ == "__main__"')

    assert content.index("def render_advanced_profile_interpretation_v3") < entrypoint
    assert content.index("def render_advanced_profile_comparison_v3") < entrypoint
