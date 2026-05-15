from pathlib import Path


def test_streamlit_has_bilingual_language_selector():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "UI_TEXT" in content
    assert "\"en\"" in content
    assert "\"fr\"" in content
    assert "key=\"language\"" in content
    assert "Francais" in content


def test_streamlit_has_politiscales_external_link():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "https://politiscales.fr/" in content
    assert 'target="_blank"' in content
    assert "Open Politiscales test" in content
    assert "Ouvrir le test Politiscales" in content


def test_streamlit_hero_no_technology_tags_and_has_better_description():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    assert "Build, compare, and interpret political profiles" in content
    assert "Creez, comparez et interpretez" in content
    assert "Python</span>" not in content
    assert "Streamlit</span>" not in content
    assert "Plotly</span>" not in content


def test_readme_mentions_bilingual_streamlit_and_politiscales():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Bilingual Streamlit interface" in content
    assert "Politiscales" in content
