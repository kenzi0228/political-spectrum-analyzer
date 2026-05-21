from pathlib import Path


APP = Path("streamlit_app.py")


def test_active_multiselect_filters_do_not_require_external_service_import():
    content = APP.read_text(encoding="utf-8")

    function_start = content.index("def _render_reference_multiselect_filters")
    function_end = content.index("def _render_advanced_profile_comparisons", function_start)
    function_body = content[function_start:function_end]

    assert "filter_reference_items_multiselect(" not in function_body
    assert "selected_filters = {" in function_body
    assert "def item_matches(item) -> bool:" in function_body


def test_active_multiselect_filters_show_filtered_count_out_of_total():
    content = APP.read_text(encoding="utf-8")

    function_start = content.index("def _render_reference_multiselect_filters")
    function_end = content.index("def _render_advanced_profile_comparisons", function_start)
    function_body = content[function_start:function_end]

    assert "total_reference_count = len(reference_items)" in function_body
    assert "reference profiles displayed" in function_body
    assert "reference profiles match the current filters" in function_body


def test_active_multiselect_filters_include_all_requested_dimensions():
    content = APP.read_text(encoding="utf-8")

    function_start = content.index("def _render_reference_multiselect_filters")
    function_end = content.index("def _render_advanced_profile_comparisons", function_start)
    function_body = content[function_start:function_end]

    for field in [
        "country",
        "ideology_family",
        "role_category",
        "gender",
        "century",
        "confidence",
    ]:
        assert f'"{field}"' in function_body

    assert "st.sidebar.multiselect" in function_body
    assert '"Role categories"' in function_body
    assert 'options=options_with_any_none("role_category")' in function_body
    assert 'key="active_reference_filter_role_category"' in function_body


def test_active_multiselect_filters_are_empty_by_default():
    content = APP.read_text(encoding="utf-8")

    function_start = content.index("def _render_reference_multiselect_filters")
    function_end = content.index("def _render_advanced_profile_comparisons", function_start)
    function_body = content[function_start:function_end]

    assert "default=[]" in function_body
    assert 'default=["Any"]' not in function_body
    assert "Reference profiles stay hidden until at least one filter is selected" in function_body
    assert "has_filter_selection = any(selected_filters.values())" in function_body
    assert "else []" in function_body
