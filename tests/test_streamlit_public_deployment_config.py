from pathlib import Path


def test_streamlit_config_exists_and_has_theme():
    path = Path(".streamlit/config.toml")

    assert path.exists()

    content = path.read_text(encoding="utf-8")

    assert "[theme]" in content
    assert "primaryColor" in content
    assert "[server]" in content
    assert "headless = true" in content


def test_streamlit_secrets_are_ignored():
    content = Path(".gitignore").read_text(encoding="utf-8")

    assert ".streamlit/secrets.toml" in content


def test_streamlit_config_readme_exists():
    path = Path(".streamlit/README.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8")

    assert "Streamlit configuration" in content
    assert "Do not commit local secrets" in content


def test_deployment_doc_mentions_public_url_and_ocr_policy():
    content = Path("docs/streamlit_cloud_deployment.md").read_text(encoding="utf-8")

    assert "Public URL" in content
    assert "https://<your-app-name>.streamlit.app" in content
    assert "OCR is intentionally excluded from the Streamlit runtime" in content
    assert "streamlit_app.py" in content


def test_readme_has_deployment_action_steps():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "## Deployment action steps" in content
    assert "Create a new app from GitHub" in content
    assert "streamlit_app.py" in content
    assert ".streamlit/config.toml" in content

def test_deployment_doc_keeps_legacy_ocr_desktop_only_phrase():
    content = Path("docs/streamlit_cloud_deployment.md").read_text(encoding="utf-8").lower()

    assert "ocr remains desktop-only" in content