from pathlib import Path


APP = Path("streamlit_app.py")
DOC = Path("docs/streamlit_plotly_default_multiselect_filters.md")
README = Path("README.md")


def test_default_reference_renderer_is_plotly():
    content = APP.read_text(encoding="utf-8")

    assert 'DEFAULT_REFERENCE_RENDERER = "plotly"' in content
    assert "render_default_reference_map" in content
    assert "render_reference_plotly_chart(reference_rows)" in content


def test_every_reference_filter_is_multiselect_capable():
    content = APP.read_text(encoding="utf-8")

    assert "REFERENCE_MULTISELECT_FILTER_FIELDS" in content
    assert '"ideology_family": "Ideology family"' in content
    assert '"role_category": "Role category"' in content
    assert '"gender": "Gender"' in content
    assert '"century": "Century"' in content
    assert '"confidence": "Confidence"' in content
    assert "st.sidebar.multiselect" in content


def test_multiselect_filter_helpers_are_available():
    content = APP.read_text(encoding="utf-8")

    assert "render_reference_multiselect_filters" in content
    assert "apply_reference_multiselect_filters" in content
    assert "render_reference_filters_and_apply" in content
    assert "_row_matches_multiselect_filter" in content


def test_plotly_default_multiselect_doc_exists():
    assert DOC.exists()

    content = DOC.read_text(encoding="utf-8")
    assert "Plotly default reference map" in content
    assert "All reference filters are multi-select" in content
    assert "gender" in content.lower()


def test_readme_mentions_plotly_default_and_multiselect_filters():
    content = README.read_text(encoding="utf-8")

    assert "Plotly default reference map" in content
    assert "multi-select reference filters" in content
