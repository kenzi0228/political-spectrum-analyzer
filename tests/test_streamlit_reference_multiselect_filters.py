
from pathlib import Path


def test_streamlit_contains_reference_multiselect_filter_ui():
    content = Path("src/political_spectrum_analyzer/streamlit_ui/reference_filters.py").read_text(encoding="utf-8")
    text_content = Path("src/political_spectrum_analyzer/streamlit_ui/text.py").read_text(encoding="utf-8")
    assert "st.multiselect" in content
    assert "reference_filters_sidebar" in content
    assert "Reference filters" in text_content
    assert "render_reference_multiselect_filters" in content


def test_streamlit_uses_runtime_self_contained_multiselect_filtering():
    content = Path("src/political_spectrum_analyzer/streamlit_ui/reference_filters.py").read_text(encoding="utf-8")
    text_content = Path("src/political_spectrum_analyzer/streamlit_ui/text.py").read_text(encoding="utf-8")

    function_start = content.index("def render_reference_multiselect_filters")
    function_body = content[function_start:]

    assert "selected_filters = {" in function_body
    assert "def item_matches(item) -> bool:" in function_body
    assert "split_filter_values" in function_body
    assert "reference_displayed_count" in function_body
    assert "reference_match_count" in function_body
    assert "reference profiles displayed" in text_content
    assert "reference profiles match the current filters" in text_content
    assert "split_filter_values" in content
    app_content = Path("streamlit_app.py").read_text(encoding="utf-8")
    assert "_render_reference_multiselect_filters(reference_personalities_for_filters, language)" in app_content
