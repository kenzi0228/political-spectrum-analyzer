from pathlib import Path


def test_streamlit_app_adds_src_to_python_path_before_package_imports():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")

    src_path_index = content.index("PACKAGE_SRC_PATH")
    package_import_index = content.index("from political_spectrum_analyzer.config import")

    assert src_path_index < package_import_index
    assert 'Path(__file__).resolve().parent / "src"' in content
    assert "sys.path.insert(0, str(PACKAGE_SRC_PATH))" in content


def test_deployment_doc_mentions_src_layout_import_path():
    content = Path("docs/streamlit_cloud_deployment.md").read_text(encoding="utf-8")

    assert "src-layout import path" in content
    assert "political_spectrum_analyzer.config" in content


def test_readme_mentions_streamlit_src_layout_import_path():
    content = Path("README.md").read_text(encoding="utf-8")

    assert "Streamlit src-layout import path" in content
    assert "src/" in content