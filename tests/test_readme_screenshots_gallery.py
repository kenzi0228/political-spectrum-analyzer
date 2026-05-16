from pathlib import Path


REQUIRED_SCREENSHOTS = [
    "docs/assets/desktop-app.png",
    "docs/assets/streamlit-home.png",
    "docs/assets/streamlit-multi-profile-chart.png",
    "docs/assets/streamlit-profile-analysis.png",
    "docs/assets/streamlit-profile-import-export.png",
]


def test_required_screenshot_files_exist():
    for screenshot in REQUIRED_SCREENSHOTS:
        assert Path(screenshot).exists(), f"Missing screenshot: {screenshot}"


def test_readme_contains_screenshot_gallery():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "## Screenshots" in content
    assert "![Desktop application](docs/assets/desktop-app.png)" in content
    assert "![Streamlit home](docs/assets/streamlit-home.png)" in content
    assert "![Multi-profile comparison](docs/assets/streamlit-multi-profile-chart.png)" in content
    assert "![Detailed profile analysis](docs/assets/streamlit-profile-analysis.png)" in content
    assert "![Profile save and import](docs/assets/streamlit-profile-import-export.png)" in content


def test_assets_readme_documents_expected_screenshots():
    content = Path("docs/assets/README.md").read_text(encoding="utf-8")

    for screenshot in REQUIRED_SCREENSHOTS:
        assert Path(screenshot).name in content

def test_readme_preserves_screenshots_to_add_legacy_anchor():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Screenshots to add" in content
    assert "docs/assets/desktop-app.png" in content
    assert "docs/assets/streamlit-home.png" in content