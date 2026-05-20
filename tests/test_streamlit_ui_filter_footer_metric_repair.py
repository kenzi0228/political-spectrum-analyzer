from pathlib import Path


APP = Path("streamlit_app.py")


def test_country_code_filter_removed_from_sidebar():
    content = APP.read_text(encoding="utf-8")
    start = content.index("def _render_reference_multiselect_filters")
    end = content.index("def _render_advanced_profile_comparisons", start)
    body = content[start:end]

    assert "active_reference_filter_country_codes" not in body
    assert '"Country code filter"' not in body
    assert '"Country codes"' not in body


def test_metric_cards_are_forced_dark():
    content = APP.read_text(encoding="utf-8")

    assert "PROFILE_METRIC_DARK_CSS" in content
    assert "_force_dark_metric_cards()" in content
    assert '[data-testid="metric-container"]' in content
    assert "#111522" in content


def test_about_content_not_called_as_global_footer_in_main():
    content = APP.read_text(encoding="utf-8")

    main_start = content.index("def main")
    entrypoint = content.rfind('if __name__ == "__main__"')
    main_body = content[main_start:entrypoint]

    assert "About this analyzer" not in main_body
