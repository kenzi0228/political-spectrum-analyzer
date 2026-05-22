from pathlib import Path
from types import SimpleNamespace

from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.streamlit_ui import profile_state


APP = Path("streamlit_app.py")
NAVIGATION = Path("src/political_spectrum_analyzer/streamlit_ui/navigation.py")
PROFILE_STATE = Path("src/political_spectrum_analyzer/streamlit_ui/profile_state.py")
PROFILE_INPUTS = Path("src/political_spectrum_analyzer/streamlit_ui/profile_inputs.py")
REFERENCE_FILTERS = Path("src/political_spectrum_analyzer/streamlit_ui/reference_filters.py")
PAGES = Path("src/political_spectrum_analyzer/streamlit_ui/pages.py")
STYLES = Path("src/political_spectrum_analyzer/streamlit_ui/styles.py")
TEXT = Path("src/political_spectrum_analyzer/streamlit_ui/text.py")


def test_sidebar_is_forced_dark_for_readability():
    content = STYLES.read_text(encoding="utf-8")
    app_content = APP.read_text(encoding="utf-8")

    assert "FORCE_DARK_SIDEBAR_CSS" in content
    assert "#0E1117" in content
    assert "#111522" in content
    assert "_force_dark_sidebar()" in app_content


def test_filters_include_any_none_and_real_value_pipeline():
    content = REFERENCE_FILTERS.read_text(encoding="utf-8")
    text_content = TEXT.read_text(encoding="utf-8")
    start = content.index("def render_reference_multiselect_filters")
    body = content[start:]

    assert '"Any"' in body
    assert '"None"' in body
    assert "default=[]" in body
    assert "has_filter_selection = any(selected_filters.values())" in body
    assert "reference_multiselect_options(reference_items, field_name)" in body
    assert "cleaned_values" in body
    assert "reference_displayed_count" in body
    assert "reference_match_count" in body
    assert "reference profiles displayed" in text_content
    assert "reference profiles match the current filters" in text_content


def test_main_uses_original_detailed_analysis_renderer():
    content = APP.read_text(encoding="utf-8")
    pages = PAGES.read_text(encoding="utf-8")
    main_start = content.index("def main")
    entrypoint = content.rfind('if __name__ == "__main__"')
    main_body = content[main_start:entrypoint]

    assert "_render_analysis(people, filtered_personalities, language)" in main_body
    assert "render_analysis(people, filtered_personalities, language)" in pages
    assert "_render_integrated_analysis_v3(people, filtered_personalities, language)" not in main_body


def test_reference_dataset_is_loaded_only_for_reference_views():
    content = APP.read_text(encoding="utf-8")
    navigation = NAVIGATION.read_text(encoding="utf-8")
    main_start = content.index("def main")
    entrypoint = content.rfind('if __name__ == "__main__"')
    main_body = content[main_start:entrypoint]

    active_view_pos = main_body.index("active_view = _render_active_view_selector(language, _t)")
    load_pos = main_body.index("personalities = _load_reference_personalities()")

    assert active_view_pos < load_pos
    assert "if _view_requires_reference_dataset(active_view):" in main_body
    assert 'return active_view in {"visualization", "reference"}' in navigation
    assert "reference_dataset_not_loaded" in main_body
    assert "Reference dataset is not loaded on this tab." in TEXT.read_text(encoding="utf-8")


def test_people_can_be_rebuilt_from_session_state_without_rendering_inputs():
    content = APP.read_text(encoding="utf-8")
    profile_state = PROFILE_STATE.read_text(encoding="utf-8")
    profile_inputs = PROFILE_INPUTS.read_text(encoding="utf-8")

    assert "def build_people_from_state()" in profile_state
    assert "PROFILE_SNAPSHOT_KEY" in profile_state
    assert "def persist_people_to_state" in profile_state
    assert "snapshot_scores.get(axis, 0)" in profile_state
    assert "persist_people_to_state(people)" in profile_inputs
    assert "people = _build_people_from_state()" in content
    assert 'key="profile_count"' in profile_inputs


def test_profile_snapshot_survives_filter_rerun_when_input_widgets_are_unmounted(monkeypatch):
    session_state = {"profile_count": 1}
    monkeypatch.setattr(profile_state, "st", SimpleNamespace(session_state=session_state))

    scores = {axis: 0 for axis in VARIABLE_NAMES}
    scores["capitalisme"] = 72
    scores["progressisme"] = 61
    person = PersonResult(name="Saved profile", scores=scores, x=1.2, y=-0.4)

    profile_state.persist_people_to_state([person])

    rebuilt = profile_state.build_people_from_state()

    assert rebuilt[0].name == "Saved profile"
    assert rebuilt[0].scores["capitalisme"] == 72
    assert rebuilt[0].scores["progressisme"] == 61


def test_streamlit_pages_are_split_from_entrypoint():
    content = APP.read_text(encoding="utf-8")
    pages = PAGES.read_text(encoding="utf-8")

    assert "render_visualization_page" in pages
    assert "render_reference_data_page" in pages
    assert "_render_visualization_page(" in content
    assert "_render_reference_data_page(" in content


def test_advanced_helpers_are_defined_before_entrypoint():
    content = APP.read_text(encoding="utf-8")
    entrypoint = content.rfind('if __name__ == "__main__"')

    assert content.index("def render_advanced_profile_interpretation_v3") < entrypoint
    assert content.index("def render_advanced_profile_comparison_v3") < entrypoint
