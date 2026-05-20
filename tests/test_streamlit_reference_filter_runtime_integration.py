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
