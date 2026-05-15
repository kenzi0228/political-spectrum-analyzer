from pathlib import Path


def test_methodology_is_detailed_enough():
    content = Path("docs/methodology.md").read_text(encoding="utf-8").lower()

    assert "weighting philosophy" in content
    assert "multi-profile comparison" in content
    assert "normalization and bounding" in content
    assert "closest-reference analysis" in content
    assert "limitations" in content


def test_methodology_explains_export_and_import():
    content = Path("docs/methodology.md").read_text(encoding="utf-8").lower()

    assert "copied-text import" in content
    assert "ocr import" in content
    assert "export methodology" in content