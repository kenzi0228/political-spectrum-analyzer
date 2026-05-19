
from pathlib import Path


def test_streamlit_contains_reference_multiselect_filter_ui():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")
    assert "st.multiselect" in content
    assert "Reference multi-select filters" in content
    assert "_render_reference_multiselect_filters" in content


def test_streamlit_uses_runtime_self_contained_multiselect_filtering():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    function_start = content.index("def _render_reference_multiselect_filters")
    function_end = content.index("def _render_advanced_profile_comparisons", function_start)
    function_body = content[function_start:function_end]

    assert "selected_filters = {" in function_body
    assert "def item_matches(item) -> bool:" in function_body
    assert "split_filter_values" in function_body
    assert "reference profiles displayed" in function_body
    assert "reference profiles match the current filters" in function_body
    assert "split_filter_values" in content
    assert "_render_reference_multiselect_filters(reference_personalities_for_filters, language)" in content
