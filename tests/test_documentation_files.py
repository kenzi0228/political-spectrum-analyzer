from pathlib import Path


def test_methodology_document_exists_and_mentions_limitations():
    path = Path("docs/methodology.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8").lower()

    assert "methodology" in content
    assert "projection" in content
    assert "limitations" in content
    assert "ocr" in content


def test_reference_dataset_document_exists_and_describes_columns():
    path = Path("docs/reference_dataset.md")

    assert path.exists()

    content = path.read_text(encoding="utf-8").lower()

    assert "reference dataset" in content
    assert "columns" in content
    assert "confidence" in content
    assert "country" in content