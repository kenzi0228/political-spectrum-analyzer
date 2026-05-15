from pathlib import Path


def test_readme_has_streamlit_web_section():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "## Web version - Streamlit" in content
    assert "Deployment ready" in content
    assert "streamlit_app.py" in content


def test_readme_documents_streamlit_features():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "English and French interface" in content
    assert "direct link to the original Politiscales test" in content
    assert "one-by-one profile save/import with JSON" in content
    assert "multi-profile comparison" in content
    assert "methodology tab explaining the formulas and coefficients" in content


def test_readme_documents_streamlit_cloud_settings():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Streamlit Community Cloud" in content
    assert "kenzi0228/political-spectrum-analyzer" in content
    assert "python-3.12" in content
    assert "requirements.txt" in content
    assert "OCR remains a desktop-only feature" in content


def test_readme_contains_post_deployment_url_placeholder():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Live demo: https://<your-app-name>.streamlit.app" in content