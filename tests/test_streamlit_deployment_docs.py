from pathlib import Path


def test_streamlit_deployment_document_exists():
    path = Path("docs/streamlit_deployment.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8").lower()

    assert "streamlit community cloud" in content
    assert "streamlit_app.py" in content
    assert "ocr" in content


def test_packages_file_is_absent_because_ocr_is_desktop_only():
    path = Path("packages.txt")

    assert not path.exists()

    deployment_doc = Path("docs/streamlit_cloud_deployment.md").read_text(encoding="utf-8").lower()

    assert "no packages.txt file is required" in deployment_doc
    assert "ocr remains desktop-only" in deployment_doc

def test_readme_mentions_web_deployment():
    path = Path("README.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8").lower()

    assert "web deployment" in content
    assert "streamlit run streamlit_app.py" in content