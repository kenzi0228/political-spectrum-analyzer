from pathlib import Path


APP = Path("streamlit_app.py")
CONTENT_PAGES = Path("src/political_spectrum_analyzer/streamlit_ui/content_pages.py")
TEXT = Path("src/political_spectrum_analyzer/streamlit_ui/text.py")


def test_streamlit_has_about_tab_translation_keys():
    content = TEXT.read_text(encoding="utf-8")

    assert '"tab_about": "About / How to use"' in content
    assert '"tab_about": "A propos / Mode d emploi"' in content
    assert "about_privacy_body" in content
    assert "about_desktop_body" in content


def test_streamlit_defines_about_renderer():
    content = (
        APP.read_text(encoding="utf-8")
        + CONTENT_PAGES.read_text(encoding="utf-8")
        + TEXT.read_text(encoding="utf-8")
    )

    assert "def render_about_tab" in content
    assert "render_politiscales_link(language, translate)" in content
    assert "about_how_to_use_body" in content


def test_streamlit_renders_about_tab():
    content = APP.read_text(encoding="utf-8")

    assert "about_tab" in content
    assert "with about_tab:" in content
    assert "_render_about_tab(language)" in content


def test_readme_mentions_about_how_to_use_page():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "About / How to use page" in content
    assert "what the analyzer does" in content
    assert "difference between the desktop and web versions" in content
