from pathlib import Path


APP = Path("streamlit_app.py")
DOC = Path("docs/advanced_personalized_interpretation_v3.md")
README = Path("README.md")


def test_advanced_interpretation_v3_helpers_exist():
    content = APP.read_text(encoding="utf-8")

    assert 'ADVANCED_INTERPRETATION_V3_VERSION = "v3"' in content
    assert "build_advanced_profile_interpretation_v3" in content
    assert "render_advanced_profile_interpretation_v3" in content


def test_interpretation_v3_uses_secondary_dimensions():
    content = APP.read_text(encoding="utf-8")

    assert "ecology" in content
    assert "productivism" in content
    assert "internationalism" in content
    assert "nationalism" in content
    assert "reformism" in content
    assert "revolution" in content


def test_interpretation_v3_has_deduplication_logic():
    content = APP.read_text(encoding="utf-8")

    assert "deduplicate_interpretation_sentences" in content
    assert "Remove repeated sentences" in content
    assert "seen = set()" in content


def test_interpretation_v3_has_quadrant_and_tension_logic():
    content = APP.read_text(encoding="utf-8")

    assert "_interpretation_v3_quadrant" in content
    assert "_interpretation_v3_tension_sentences" in content
    assert "left-libertarian" in content
    assert "right-authoritarian" in content


def test_advanced_interpretation_v3_doc_exists():
    assert DOC.exists()

    content = DOC.read_text(encoding="utf-8")
    assert "Advanced personalized interpretation v3" in content
    assert "Non-repetition rule" in content
    assert "Secondary dimensions" in content


def test_readme_mentions_advanced_interpretation_v3():
    content = README.read_text(encoding="utf-8")

    assert "Advanced personalized interpretation v3" in content
