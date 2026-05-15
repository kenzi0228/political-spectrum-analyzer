from pathlib import Path


def test_streamlit_cloud_deployment_doc_exists():
    path = Path("docs/streamlit_cloud_deployment.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8").lower()

    assert "streamlit community cloud" in content
    assert "streamlit_app.py" in content
    assert "ocr remains desktop-only" in content


def test_runtime_txt_declares_python_version():
    path = Path("runtime.txt")

    assert path.exists()

    content = path.read_text(encoding="utf-8").strip()

    assert content.startswith("python-3.12")


def test_streamlit_app_does_not_import_ocr_runtime():
    content = Path("streamlit_app.py").read_text(encoding="utf-8").lower()

    assert "extract_scores_from_image" not in content
    assert "pytesseract" not in content
    assert "politiscales_ocr" not in content


def test_requirements_include_streamlit_stack():
    content = Path("requirements.txt").read_text(encoding="utf-8").lower()

    assert "streamlit" in content
    assert "plotly" in content
    assert "pandas" in content


def test_readme_mentions_live_streamlit_demo_placeholder():
    content = Path("README.md").read_text(encoding="utf-8").lower()

    assert "live streamlit demo" in content
    assert "deployment ready" in content
    assert "docs/streamlit_cloud_deployment.md" in content