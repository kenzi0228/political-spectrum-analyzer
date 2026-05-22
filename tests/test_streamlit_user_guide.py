from pathlib import Path


APP = Path("streamlit_app.py")
TEXT = Path("src/political_spectrum_analyzer/streamlit_ui/text.py")


def test_streamlit_app_has_user_guide_tab():
    content = APP.read_text(encoding="utf-8") + TEXT.read_text(encoding="utf-8")

    assert "def _render_user_guide_tab" in content
    assert '"Guide"' in content
    assert "with guide_tab:" in content


def test_user_guide_mentions_profile_workflow():
    content = APP.read_text(encoding="utf-8") + TEXT.read_text(encoding="utf-8")

    assert "Step 1 - Enter scores" in content
    assert "Step 2 - Read the graph" in content
    assert "Step 3 - Save or export" in content
    assert "Profile save and import" in content
    assert "Manual numeric entry" in content


def test_readme_mentions_streamlit_user_guide():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Streamlit user guide" in content
    assert "Guide tab" in content
