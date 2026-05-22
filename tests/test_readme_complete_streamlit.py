from pathlib import Path


def test_readme_has_project_status_and_interfaces():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Desktop version: stable" in content
    assert "Streamlit version: deployment ready" in content
    assert "v1.1.0-streamlit" in content
    assert "v1.0.0-desktop" in content


def test_readme_has_streamlit_web_section():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "## Web version - Streamlit" in content
    assert "Deployment ready" in content
    assert "streamlit_app.py" in content
    assert "Live demo: https://<your-app-name>.streamlit.app" in content


def test_readme_documents_streamlit_features():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "English and French interface" in content
    assert "direct link to the original Politiscales test" in content
    assert "one-by-one profile save/import with JSON" in content
    assert "multi-profile comparison" in content
    assert "methodology tab explaining the formulas and coefficients" in content


def test_readme_documents_model_coefficients():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "0.90 * communisme" in content
    assert "0.70 * regulation" in content
    assert "0.12 * (productivisme - ecologie)" in content
    assert "sigmoid_scaled" in content


def test_readme_documents_architecture_and_assets():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "docs/assets/" in content
    assert "src/" in content
    assert "profile_interpretation_service.py" in content
    assert "streamlit_cloud_deployment.md" in content


def test_readme_mentions_non_commercial_license():
    content = Path("README.md").read_text(encoding="utf-8").lower()

    assert "custom non-commercial license" in content
    assert "commercial use" in content


def test_readme_keeps_legacy_documentation_anchors():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "## Running the application" in content
    assert "Bilingual Streamlit interface" in content
    assert "Live Streamlit demo" in content
    assert "Web deployment" in content
    assert "Streamlit user guide" in content

def test_readme_keeps_remaining_legacy_anchors():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Limitations" in content
    assert "Guide tab" in content
