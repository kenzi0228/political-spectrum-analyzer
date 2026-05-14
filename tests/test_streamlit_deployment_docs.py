from pathlib import Path


def test_streamlit_deployment_document_exists():
    path = Path("docs/streamlit_deployment.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8").lower()

    assert "streamlit community cloud" in content
    assert "streamlit_app.py" in content
    assert "ocr" in content


def test_packages_file_exists_and_documents_ocr_decision():
    path = Path("packages.txt")

    assert path.exists()

    content = path.read_text(encoding="utf-8").lower()

    assert "tesseract" in content
    assert "desktop-only" in content


def test_readme_mentions_web_deployment():
    path = Path("README.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8").lower()

    assert "web deployment" in content
    assert "streamlit run streamlit_app.py" in content