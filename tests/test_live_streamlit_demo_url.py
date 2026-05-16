from pathlib import Path


LIVE_URL = "https://political-spectrum-analyzer.streamlit.app/"


def test_readme_contains_live_streamlit_demo_url():
    content = Path("README.md").read_text(encoding="utf-8")

    assert LIVE_URL in content or LIVE_URL.rstrip("/") in content
    assert "Live demo" in content


def test_deployment_doc_contains_live_streamlit_demo_url():
    content = Path("docs/streamlit_cloud_deployment.md").read_text(encoding="utf-8")

    assert LIVE_URL in content or LIVE_URL.rstrip("/") in content


def test_deployment_template_is_preserved_for_future_forks():
    readme = Path("README.md").read_text(encoding="utf-8")
    deployment_doc = Path("docs/streamlit_cloud_deployment.md").read_text(encoding="utf-8")

    assert "Live demo: https://<your-app-name>.streamlit.app" in readme
    assert "https://<your-app-name>.streamlit.app" in deployment_doc


def test_readme_keeps_deployment_ready_legacy_anchor():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Deployment ready" in content
