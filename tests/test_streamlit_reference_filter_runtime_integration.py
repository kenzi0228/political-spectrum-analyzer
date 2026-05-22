from pathlib import Path


APP = Path("streamlit_app.py")
REFERENCE_FILTERS = Path("src/political_spectrum_analyzer/streamlit_ui/reference_filters.py")
TEXT = Path("src/political_spectrum_analyzer/streamlit_ui/text.py")


def test_active_multiselect_filters_do_not_require_external_service_import():
    content = REFERENCE_FILTERS.read_text(encoding="utf-8")

    function_start = content.index("def render_reference_multiselect_filters")
    function_body = content[function_start:]

    assert "filter_reference_items_multiselect(" not in function_body
    assert "selected_filters = {" in function_body
    assert "def item_matches(item) -> bool:" in function_body


def test_active_multiselect_filters_show_filtered_count_out_of_total():
    content = REFERENCE_FILTERS.read_text(encoding="utf-8")
    text_content = TEXT.read_text(encoding="utf-8")

    function_start = content.index("def render_reference_multiselect_filters")
    function_body = content[function_start:]

    assert "total_reference_count = len(reference_items)" in function_body
    assert "reference_displayed_count" in function_body
    assert "reference_match_count" in function_body
    assert "reference profiles displayed" in text_content
    assert "reference profiles match the current filters" in text_content


def test_active_multiselect_filters_include_all_requested_dimensions():
    content = REFERENCE_FILTERS.read_text(encoding="utf-8")

    function_start = content.index("def render_reference_multiselect_filters")
    function_body = content[function_start:]

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
    assert '"filter_role_categories"' in function_body
    assert '"Role categories"' in TEXT.read_text(encoding="utf-8")
    assert 'options=options_with_any_none("role_category")' in function_body
    assert 'key="active_reference_filter_role_category"' in function_body


def test_active_multiselect_filters_are_empty_by_default():
    content = REFERENCE_FILTERS.read_text(encoding="utf-8")
    text_content = TEXT.read_text(encoding="utf-8")

    function_start = content.index("def render_reference_multiselect_filters")
    function_body = content[function_start:]

    assert "default=[]" in function_body
    assert 'default=["Any"]' not in function_body
    assert "reference_filters_hidden_caption" in function_body
    assert "Reference profiles stay hidden until at least one filter is selected" in text_content
    assert "has_filter_selection = any(selected_filters.values())" in function_body
    assert "else []" in function_body
