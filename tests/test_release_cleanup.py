from pathlib import Path


def test_gitignore_contains_release_cleanup_rules():
    content = Path(".gitignore").read_text(encoding="utf-8")

    assert ".venv/" in content
    assert "*.egg-info/" in content
    assert "outputs/ocr_debug/" in content
    assert "commit_*.ps1" in content


def test_release_notes_exist():
    path = Path("docs/release_notes_v1.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8").lower()

    assert "desktop" in content
    assert "streamlit" in content
    assert "known limitations" in content


def test_release_checklist_exists():
    path = Path("docs/release_checklist.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8").lower()

    assert "python -m pytest" in content
    assert "streamlit run streamlit_app.py" in content
    assert "git tag v1.0.0" in content


def test_sensitive_ocr_debug_folder_is_not_present_locally():
    assert not Path("outputs/ocr_debug").exists()