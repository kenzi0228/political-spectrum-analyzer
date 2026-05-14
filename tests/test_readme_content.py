from pathlib import Path


def test_readme_exists_and_contains_core_sections():
    path = Path("README.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8").lower()

    assert "political spectrum analyzer" in content
    assert "installation" in content
    assert "running the application" in content
    assert "methodology" in content
    assert "reference dataset" in content
    assert "limitations" in content


def test_readme_mentions_testing_and_csv_export():
    content = Path("README.md").read_text(encoding="utf-8").lower()

    assert "pytest" in content
    assert "csv export" in content
    assert "ocr" in content