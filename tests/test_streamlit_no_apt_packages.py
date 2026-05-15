from pathlib import Path


def test_streamlit_deployment_does_not_ship_packages_txt():
    assert not Path("packages.txt").exists()


def test_deployment_docs_explain_no_apt_packages_policy():
    content = Path("docs/streamlit_cloud_deployment.md").read_text(encoding="utf-8")

    assert "No packages.txt file is required" in content
    assert "OCR remains desktop-only" in content
    assert "requirements.txt" in content


def test_readme_explains_no_streamlit_system_packages():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "No packages.txt file is required" in content
    assert "OCR remains desktop-only" in content