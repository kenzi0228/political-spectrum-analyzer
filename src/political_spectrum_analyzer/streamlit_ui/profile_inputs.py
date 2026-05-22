"""Profile input widgets for the Streamlit app."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime

import streamlit as st

from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.services.text_import_service import extract_scores_from_text
from political_spectrum_analyzer.streamlit_ui.profile_state import (
    build_person_result,
    persist_people_to_state,
    profile_state_prefix,
)


Translate = Callable[[str, str], str]


def format_variable_name(variable_name: str) -> str:
    return variable_name.replace("_", " ").capitalize()


def default_scores() -> dict[str, int]:
    return {variable: 0 for variable in VARIABLE_NAMES}


def profile_payload(person: PersonResult) -> dict[str, object]:
    return {
        "schema": "political_spectrum_profile.v1",
        "saved_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "name": person.name,
        "scores": {axis: int(person.scores.get(axis, 0)) for axis in VARIABLE_NAMES},
    }


def apply_profile_payload_to_state(profile_index: int, payload: dict[str, object]) -> None:
    prefix = profile_state_prefix(profile_index)
    name = str(payload.get("name", f"Profile {profile_index + 1}"))
    raw_scores = payload.get("scores", {})

    if not isinstance(raw_scores, dict):
        raise ValueError("Invalid profile file: 'scores' must be an object.")

    st.session_state[f"{prefix}_name"] = name

    for axis in VARIABLE_NAMES:
        value = int(raw_scores.get(axis, 0))
        st.session_state[f"{prefix}_{axis}"] = max(0, min(100, value))


def _t(translate: Translate, key: str) -> str:
    return translate(st.session_state.get("language", "en"), key)


def render_score_inputs(
    imported_scores: dict[str, int] | None,
    widget_prefix: str,
    precise_input_mode: bool,
) -> dict[str, int]:
    scores = imported_scores or default_scores()
    output_scores: dict[str, int] = {}

    categories = {
        "Social and cultural": [
            "constructivisme",
            "essentialisme",
            "progressisme",
            "conservatisme",
        ],
        "Justice and international orientation": [
            "justice_rehabilitative",
            "justice_punitive",
            "internationalisme",
            "nationalisme",
        ],
        "Economic and ecological": [
            "communisme",
            "capitalisme",
            "regulation",
            "laissez_faire",
            "ecologie",
            "productivisme",
        ],
        "Political strategy": [
            "revolution",
            "reformisme",
        ],
    }

    for category, variables in categories.items():
        with st.expander(category, expanded=True):
            cols = st.columns(2)

            for index, variable in enumerate(variables):
                key = f"{widget_prefix}_{variable}"
                if key not in st.session_state:
                    st.session_state[key] = int(scores.get(variable, 0))

                with cols[index % 2]:
                    if precise_input_mode:
                        output_scores[variable] = int(
                            st.number_input(
                                format_variable_name(variable),
                                min_value=0,
                                max_value=100,
                                step=1,
                                key=key,
                            )
                        )
                    else:
                        output_scores[variable] = int(
                            st.slider(
                                format_variable_name(variable),
                                min_value=0,
                                max_value=100,
                                step=1,
                                key=key,
                            )
                        )

    for variable in VARIABLE_NAMES:
        output_scores.setdefault(variable, int(scores.get(variable, 0)))

    return output_scores


def render_profile_import_controls(profile_index: int, translate: Translate) -> None:
    prefix = profile_state_prefix(profile_index)

    if f"{prefix}_upload_nonce" not in st.session_state:
        st.session_state[f"{prefix}_upload_nonce"] = 0

    with st.expander(_t(translate, "import_saved_profile"), expanded=False):
        uploaded_file = st.file_uploader(
            _t(translate, "select_saved_json"),
            type=["json"],
            key=f"{prefix}_json_upload_{st.session_state[f'{prefix}_upload_nonce']}",
        )

        if uploaded_file is not None:
            if st.button(_t(translate, "load_this_profile"), key=f"{prefix}_load_json"):
                try:
                    payload = json.loads(uploaded_file.getvalue().decode("utf-8"))
                    apply_profile_payload_to_state(profile_index, payload)

                    # Change the uploader key on rerun so the uploaded file is released from the UI.
                    st.session_state[f"{prefix}_upload_nonce"] += 1
                    st.success(_t(translate, "profile_loaded"))
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not load this profile file: {exc}")


def render_profile_import_export(
    profile_index: int,
    current_person: PersonResult | None,
    translate: Translate,
) -> None:
    prefix = profile_state_prefix(profile_index)

    with st.expander(_t(translate, "save_this_profile"), expanded=False):
        if current_person is not None:
            payload = profile_payload(current_person)
            safe_name = current_person.name.lower().replace(" ", "_").replace("/", "_")

            st.download_button(
                label=_t(translate, "download_profile_json"),
                data=json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8"),
                file_name=f"{safe_name or 'profile'}_profile.json",
                mime="application/json",
                key=f"{prefix}_download_json",
                use_container_width=True,
            )

            st.caption(_t(translate, "profile_save_caption"))


def render_profile_input(
    profile_index: int,
    precise_input_mode: bool,
    translate: Translate,
) -> PersonResult:
    widget_prefix = profile_state_prefix(profile_index)

    st.markdown(f"### {_t(translate, 'profile_heading').format(number=profile_index + 1)}")

    render_profile_import_controls(profile_index, translate)

    if f"{widget_prefix}_name" not in st.session_state:
        st.session_state[f"{widget_prefix}_name"] = f"Profile {profile_index + 1}"

    profile_name = st.text_input(
        "Profile name",
        key=f"{widget_prefix}_name",
    )

    imported_scores = None

    with st.expander(_t(translate, "copied_text_import"), expanded=False):
        copied_text = st.text_area(
            _t(translate, "paste_results_text"),
            height=200,
            key=f"{widget_prefix}_copied_text",
            placeholder=(
                "Constructivisme\n"
                "Essentialisme\n"
                "7%\n"
                "26%\n"
                "67%"
            ),
        )

        if copied_text.strip():
            imported_scores = extract_scores_from_text(copied_text)
            detected_count = sum(1 for value in imported_scores.values() if value != 0)
            st.success(_t(translate, "copied_scores_detected").format(count=detected_count))

            if st.button(_t(translate, "apply_copied_scores"), key=f"{widget_prefix}_apply_text"):
                for axis in VARIABLE_NAMES:
                    st.session_state[f"{widget_prefix}_{axis}"] = int(imported_scores.get(axis, 0))
                st.rerun()

    scores = render_score_inputs(
        imported_scores=imported_scores,
        widget_prefix=widget_prefix,
        precise_input_mode=precise_input_mode,
    )

    person = build_person_result(profile_name, scores)
    render_profile_import_export(profile_index, person, translate)

    return person


def render_multi_profile_inputs(precise_input_mode: bool, translate: Translate) -> list[PersonResult]:
    language = st.session_state.get("language", "en")
    st.header(translate(language, "input_header"))
    st.markdown(
        '<p class="small-muted">' + translate(language, "input_intro") + "</p>",
        unsafe_allow_html=True,
    )

    profile_count = st.number_input(
        translate(language, "profile_count_label"),
        min_value=1,
        max_value=8,
        value=1,
        step=1,
        help=translate(language, "profile_count_help"),
        key="profile_count",
    )

    people: list[PersonResult] = []

    if int(profile_count) == 1:
        people.append(render_profile_input(0, precise_input_mode, translate))
        persist_people_to_state(people)
        return people

    tabs = st.tabs([
        translate(language, "profile_heading").format(number=index + 1)
        for index in range(int(profile_count))
    ])

    for index, tab in enumerate(tabs):
        with tab:
            people.append(render_profile_input(index, precise_input_mode, translate))

    persist_people_to_state(people)
    return people
