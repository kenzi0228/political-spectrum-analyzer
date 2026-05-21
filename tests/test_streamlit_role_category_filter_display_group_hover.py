from pathlib import Path


APP = Path("streamlit_app.py")


def test_streamlit_uses_role_category_as_reference_filter_dimension():
    content = APP.read_text(encoding="utf-8")

    assert "role_category" in content
    assert "Role category" in content or "role category" in content
    assert '"role_category": ["role_category", "role", "category"]' in content
    assert 'options=options_with_any_none("role_category")' in content


def test_streamlit_keeps_display_group_as_hover_metadata():
    content = APP.read_text(encoding="utf-8")

    assert "display_group" in content
    assert "REFERENCE_TOOLTIP_FIELDS" in content
