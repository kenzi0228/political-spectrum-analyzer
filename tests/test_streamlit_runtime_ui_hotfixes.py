from pathlib import Path


APP = Path("streamlit_app.py")


def test_sidebar_is_forced_dark_for_readability():
    content = APP.read_text(encoding="utf-8")

    assert "FORCE_DARK_SIDEBAR_CSS" in content
    assert "#0E1117" in content
    assert "#111522" in content
    assert "_force_dark_sidebar()" in content


def test_filters_include_any_and_none_options():
    content = APP.read_text(encoding="utf-8")
    start = content.index("def _render_reference_multiselect_filters")
    end = content.index("def _render_advanced_profile_comparisons", start)
    body = content[start:end]

    assert '"Any"' in body
    assert '"None"' in body
    assert 'default=["Any"]' in body
    assert "reference profiles displayed" in body
    assert "reference profiles match the current filters" in body


def test_integrated_analysis_no_longer_calls_late_defined_v3_renderer():
    content = APP.read_text(encoding="utf-8")
    start = content.index("def _render_integrated_analysis_v3")
    end = content.index("\ndef main", start)
    body = content[start:end]

    assert "render_advanced_profile_interpretation_v3(" not in body
    assert "render_advanced_profile_comparison_v3(" not in body
