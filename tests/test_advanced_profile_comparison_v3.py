from pathlib import Path


APP = Path("streamlit_app.py")
DOC = Path("docs/advanced_profile_comparison_v3.md")
README = Path("README.md")


def test_advanced_comparison_v3_helpers_exist():
    content = APP.read_text(encoding="utf-8")

    assert 'ADVANCED_COMPARISON_V3_VERSION = "v3"' in content
    assert "build_advanced_profile_comparison_v3" in content
    assert "render_advanced_profile_comparison_v3" in content


def test_advanced_comparison_v3_has_distance_and_compatibility():
    content = APP.read_text(encoding="utf-8")

    assert "_comparison_v3_distance" in content
    assert "_comparison_v3_compatibility_score" in content
    assert "compatibility_score" in content


def test_advanced_comparison_v3_uses_ranked_gaps_and_secondary_dimensions():
    content = APP.read_text(encoding="utf-8")

    assert "_comparison_v3_ranked_gaps" in content
    assert "_comparison_v3_secondary_gap_sentences" in content
    assert "ecology" in content
    assert "internationalism" in content
    assert "reformism" in content


def test_advanced_comparison_v3_has_deduplication_logic():
    content = APP.read_text(encoding="utf-8")

    assert "deduplicate_comparison_sentences" in content
    assert "Remove repeated sentences from comparison text" in content


def test_advanced_comparison_v3_doc_exists():
    assert DOC.exists()

    content = DOC.read_text(encoding="utf-8")
    assert "Advanced profile comparison v3" in content
    assert "Compatibility score" in content
    assert "Ranked gaps" in content


def test_readme_mentions_advanced_comparison_v3():
    content = README.read_text(encoding="utf-8")

    assert "Advanced profile comparison v3" in content
