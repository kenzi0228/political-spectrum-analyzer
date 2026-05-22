from pathlib import Path


APP = Path("streamlit_app.py")
REFERENCE_FILTERS = Path("src/political_spectrum_analyzer/streamlit_ui/reference_filters.py")


def test_split_filter_values_defined_before_reference_options():
    content = REFERENCE_FILTERS.read_text(encoding="utf-8")

    split_index = content.index("def split_filter_values(")
    options_index = content.index("def reference_multiselect_options")

    assert split_index < options_index


def test_split_filter_values_supports_commas_semicolons_and_lists():
    content = REFERENCE_FILTERS.read_text(encoding="utf-8")

    assert "replace(\",\", \";\")" in content
    assert "isinstance(value, (list, tuple, set))" in content
    assert "return values" in content
