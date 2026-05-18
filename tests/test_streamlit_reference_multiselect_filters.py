
from pathlib import Path


def test_streamlit_contains_reference_multiselect_filter_ui():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")
    assert "st.multiselect" in content
    assert "Reference multi-select filters" in content
    assert "_render_reference_multiselect_filters" in content


def test_streamlit_uses_multiselect_filter_service():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")
    assert "filter_reference_items_multiselect" in content
    assert "split_filter_values" in content
    assert "_render_reference_multiselect_filters(reference_personalities_for_filters, language)" in content
