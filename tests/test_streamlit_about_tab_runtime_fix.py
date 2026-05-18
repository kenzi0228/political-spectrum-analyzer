from pathlib import Path


APP = Path("streamlit_app.py")


def test_about_tab_has_runtime_fallback_before_use():
    content = APP.read_text(encoding="utf-8")

    assert "with about_tab:" in content
    assert "about_tab = locals().get(" in content

    fallback_pos = content.index("about_tab = locals().get(")
    use_pos = content.index("with about_tab:")

    assert fallback_pos < use_pos
