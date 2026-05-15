from __future__ import annotations

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from political_spectrum_analyzer.config import PERSONALITIES_CSV_PATH
from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.model.transforms import apply_transformations_and_get_coordinates
from political_spectrum_analyzer.services.analysis_service import analyze_profile
from political_spectrum_analyzer.services.export_results_service import build_export_rows
from political_spectrum_analyzer.services.personalities_service import load_personalities
from political_spectrum_analyzer.services.profile_interpretation_service import interpret_profile
from political_spectrum_analyzer.services.personality_filter_service import (
    NONE_VALUE,
    filter_personalities,
    get_unique_values,
)
from political_spectrum_analyzer.services.text_import_service import extract_scores_from_text
from political_spectrum_analyzer.web.plotly_plot import build_political_spectrum_figure


st.set_page_config(
    page_title="Political Spectrum Analyzer",
    page_icon=":bar_chart:",
    layout="wide",
)


CUSTOM_CSS = """
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

.hero-card {
    padding: 1.4rem 1.6rem;
    border-radius: 18px;
    border: 1px solid rgba(37, 99, 235, 0.16);
    background: linear-gradient(135deg, #eff6ff 0%, #ffffff 55%, #f8fafc 100%);
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
    margin-bottom: 1rem;
}

.hero-title {
    font-size: 2.15rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 0.35rem;
}

.hero-subtitle {
    font-size: 1.02rem;
    color: #475569;
    line-height: 1.55;
    max-width: 1050px;
}

.feature-pill {
    display: inline-block;
    padding: 0.3rem 0.65rem;
    margin: 0.25rem 0.25rem 0.25rem 0;
    border-radius: 999px;
    background: #dbeafe;
    color: #1e3a8a;
    font-size: 0.82rem;
    font-weight: 600;
}

.warning-box {
    padding: 0.85rem 1rem;
    border-radius: 14px;
    border-left: 4px solid #2563EB;
    background: #eff6ff;
    color: #1e3a8a;
    margin: 1rem 0;
}

.small-muted {
    color: #64748b;
    font-size: 0.9rem;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e2e8f0;
    padding: 0.8rem;
    border-radius: 14px;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.04);
}

/* Make metric cards readable when values are long, especially quadrant labels. */
div[data-testid="stMetric"] {
    min-height: 118px;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.86rem;
    color: #334155;
}

div[data-testid="stMetricValue"] {
    font-size: 1.42rem;
    line-height: 1.15;
    white-space: normal;
    overflow-wrap: anywhere;
    word-break: normal;
}

div[data-testid="stMetricValue"] > div {
    white-space: normal;
    overflow-wrap: anywhere;
    word-break: normal;
}

section[data-testid="stSidebar"] {
    background-color: #f8fafc;
}
</style>
"""


def _inject_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _format_variable_name(variable_name: str) -> str:
    return variable_name.replace("_", " ").capitalize()


@st.cache_data
def _load_reference_personalities():
    return load_personalities(PERSONALITIES_CSV_PATH)


def _default_scores() -> dict[str, int]:
    return {variable: 0 for variable in VARIABLE_NAMES}


def _profile_state_prefix(profile_index: int) -> str:
    return f"profile_{profile_index}"


def _build_person_result(profile_name: str, scores: dict[str, int]) -> PersonResult:
    x, y = apply_transformations_and_get_coordinates(scores)

    return PersonResult(
        name=profile_name.strip() or "Profile",
        scores=scores,
        x=float(x),
        y=float(y),
    )


def _profile_payload(person: PersonResult) -> dict[str, object]:
    return {
        "schema": "political_spectrum_profile.v1",
        "saved_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "name": person.name,
        "scores": {axis: int(person.scores.get(axis, 0)) for axis in VARIABLE_NAMES},
    }


def _apply_profile_payload_to_state(profile_index: int, payload: dict[str, object]) -> None:
    prefix = _profile_state_prefix(profile_index)
    name = str(payload.get("name", f"Profile {profile_index + 1}"))
    raw_scores = payload.get("scores", {})

    if not isinstance(raw_scores, dict):
        raise ValueError("Invalid profile file: 'scores' must be an object.")

    st.session_state[f"{prefix}_name"] = name

    for axis in VARIABLE_NAMES:
        value = int(raw_scores.get(axis, 0))
        st.session_state[f"{prefix}_{axis}"] = max(0, min(100, value))


def _render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Political Spectrum Analyzer</div>
            <div class="hero-subtitle">
                Build, compare, and interpret political profiles from 16 ideological scores.
                Enter one or several profiles, project them on the spectrum, compare them with
                reference personalities, and get a detailed score-based reading of each profile.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="warning-box">
            Start by entering a profile manually or importing copied Politiscales-style results.
            The app then shows the graph position, closest references, and a personalized analysis
            based on the strongest and weakest axes.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_single_profile_analysis(person: PersonResult, personalities) -> None:
    analysis = analyze_profile(person=person, personalities=personalities, top_n=3)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("x coordinate", f"{analysis.x:.3f}")
    col2.metric("y coordinate", f"{analysis.y:.3f}")
    col3.metric("Quadrant", analysis.quadrant)
    col4.metric("Distance to center", f"{analysis.distance_to_center:.3f}")

    closest_data = [
        {
            "Rank": index,
            "Name": match.name,
            "Group": match.display_group,
            "Distance": match.distance,
            "x": match.x,
            "y": match.y,
        }
        for index, match in enumerate(analysis.closest_references, start=1)
    ]

    st.dataframe(pd.DataFrame(closest_data), use_container_width=True, hide_index=True)
    _render_profile_interpretation(person)


def _render_profile_interpretation(person: PersonResult) -> None:
    interpretation = interpret_profile(
        profile_name=person.name,
        scores=person.scores,
    )

    st.markdown("#### Personalized profile reading")
    st.success(interpretation.archetype)
    st.write(interpretation.synthesis)

    reading_col1, reading_col2, reading_col3 = st.columns(3)
    reading_col1.info(interpretation.economic_reading)
    reading_col2.info(interpretation.societal_reading)
    reading_col3.info(interpretation.strategic_reading)

    st.info(interpretation.tension_reading)

    if interpretation.profile_highlights:
        st.markdown("#### Profile highlights")
        for highlight in interpretation.profile_highlights:
            st.markdown(f"- {highlight}")

    dominant_rows = [
        {
            "Axis": axis.label,
            "Score": axis.score,
            "Level": axis.level,
            "Meaning": axis.interpretation,
        }
        for axis in interpretation.dominant_axes
    ]

    weak_rows = [
        {
            "Axis": axis.label,
            "Score": axis.score,
            "Level": axis.level,
            "Meaning": axis.interpretation,
        }
        for axis in interpretation.weak_axes
    ]

    balance_rows = [
        {
            "Dimension": row["dimension"],
            "First pole": row["left_axis"],
            "First score": row["left_score"],
            "Second pole": row["right_axis"],
            "Second score": row["right_score"],
            "Leading tendency": row["leading_side"],
            "Reading": row["reading"],
        }
        for row in interpretation.axis_pair_balances
    ]

    st.markdown("#### Dominant axes")
    st.dataframe(pd.DataFrame(dominant_rows), use_container_width=True, hide_index=True)

    st.markdown("#### Weakest axes")
    st.dataframe(pd.DataFrame(weak_rows), use_container_width=True, hide_index=True)

    st.markdown("#### Axis-by-axis balance")
    st.dataframe(pd.DataFrame(balance_rows), use_container_width=True, hide_index=True)


def _render_analysis(people: list[PersonResult], personalities) -> None:
    if not people:
        st.info("No profile available for analysis.")
        return

    if len(people) == 1:
        st.subheader(f"Analysis - {people[0].name}")
        _render_single_profile_analysis(people[0], personalities)
        return

    st.subheader("Multi-profile analysis")

    summary_rows = []
    for person in people:
        analysis = analyze_profile(person=person, personalities=personalities, top_n=3)
        interpretation = interpret_profile(profile_name=person.name, scores=person.scores)

        closest = analysis.closest_references[0].name if analysis.closest_references else ""

        summary_rows.append(
            {
                "Profile": analysis.name,
                "Profile type": interpretation.archetype,
                "x": analysis.x,
                "y": analysis.y,
                "Quadrant": analysis.quadrant,
                "Distance to center": analysis.distance_to_center,
                "Closest reference": closest,
            }
        )

    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    st.markdown("### Details by profile")
    for person in people:
        with st.expander(person.name, expanded=False):
            _render_single_profile_analysis(person, personalities)


def _render_reference_filters(personalities):
    st.sidebar.header("Controls")
    st.sidebar.subheader("Reference filters")

    group = st.sidebar.selectbox(
        "Group",
        get_unique_values(personalities, "display_group"),
        index=0,
        help="None hides references by default. Any displays all values for this dimension.",
    )

    country = st.sidebar.selectbox(
        "Country",
        get_unique_values(personalities, "country"),
        index=0,
    )

    period = st.sidebar.selectbox(
        "Period",
        get_unique_values(personalities, "period"),
        index=0,
    )

    ideology = st.sidebar.selectbox(
        "Ideology",
        get_unique_values(personalities, "ideology_family"),
        index=0,
    )

    filtered = filter_personalities(
        personalities=personalities,
        display_group=group,
        country=country,
        period=period,
        ideology_family=ideology,
    )

    st.sidebar.metric("Displayed references", f"{len(filtered)} / {len(personalities)}")

    if group == NONE_VALUE and country == NONE_VALUE and period == NONE_VALUE and ideology == NONE_VALUE:
        st.sidebar.info("Set one filter to Any or to a specific value to display references.")

    return filtered


def _render_sidebar_export_options():
    st.sidebar.subheader("Export options")

    export_mode = st.sidebar.selectbox(
        "CSV export mode",
        [
            "profiles_only",
            "closest_references",
            "all_references",
            "filtered_references",
        ],
        format_func=lambda value: {
            "profiles_only": "Profiles only",
            "closest_references": "Profiles + closest references",
            "all_references": "Profiles + all references",
            "filtered_references": "Profiles + current filtered references",
        }[value],
    )

    closest_count = st.sidebar.number_input(
        "Closest references count",
        min_value=1,
        max_value=20,
        value=3,
        step=1,
    )

    precise_input_mode = st.sidebar.toggle(
        "Manual numeric entry",
        value=True,
        help="On: type exact values for each axis. Off: adjust scores with sliders.",
    )

    return export_mode, int(closest_count), precise_input_mode


def _render_score_inputs(
    imported_scores: dict[str, int] | None,
    widget_prefix: str,
    precise_input_mode: bool,
) -> dict[str, int]:
    scores = imported_scores or _default_scores()

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
                                _format_variable_name(variable),
                                min_value=0,
                                max_value=100,
                                step=1,
                                key=key,
                            )
                        )
                    else:
                        output_scores[variable] = int(
                            st.slider(
                                _format_variable_name(variable),
                                min_value=0,
                                max_value=100,
                                step=1,
                                key=key,
                            )
                        )

    for variable in VARIABLE_NAMES:
        output_scores.setdefault(variable, int(scores.get(variable, 0)))

    return output_scores


def _render_profile_import_export(profile_index: int, current_person: PersonResult | None) -> None:
    prefix = _profile_state_prefix(profile_index)

    with st.expander("Save or import this profile", expanded=False):
        uploaded_file = st.file_uploader(
            "Import a saved profile JSON",
            type=["json"],
            key=f"{prefix}_json_upload",
        )

        if uploaded_file is not None:
            if st.button("Load saved profile into this form", key=f"{prefix}_load_json"):
                try:
                    payload = json.loads(uploaded_file.getvalue().decode("utf-8"))
                    _apply_profile_payload_to_state(profile_index, payload)
                    st.success("Saved profile loaded. You can now edit the values before exporting again.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not load this profile file: {exc}")

        if current_person is not None:
            payload = _profile_payload(current_person)
            safe_name = current_person.name.lower().replace(" ", "_").replace("/", "_")
            st.download_button(
                label="Download this profile JSON",
                data=json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8"),
                file_name=f"{safe_name or 'profile'}_profile.json",
                mime="application/json",
                key=f"{prefix}_download_json",
                use_container_width=True,
            )

            st.caption(
                "Profile save/import is currently local and file-based. A future authenticated version can store profiles per user account."
            )


def _render_profile_input(profile_index: int, precise_input_mode: bool) -> PersonResult:
    widget_prefix = _profile_state_prefix(profile_index)

    st.markdown(f"### Profile {profile_index + 1}")

    if f"{widget_prefix}_name" not in st.session_state:
        st.session_state[f"{widget_prefix}_name"] = f"Profile {profile_index + 1}"

    profile_name = st.text_input(
        "Profile name",
        key=f"{widget_prefix}_name",
    )

    imported_scores = None

    with st.expander("Import from copied Politiscales-style text", expanded=False):
        copied_text = st.text_area(
            "Paste copied results text",
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
            st.success(f"{detected_count}/16 non-zero scores detected from copied text.")

            if st.button("Apply copied-text scores to this profile", key=f"{widget_prefix}_apply_text"):
                for axis in VARIABLE_NAMES:
                    st.session_state[f"{widget_prefix}_{axis}"] = int(imported_scores.get(axis, 0))
                st.rerun()

    scores = _render_score_inputs(
        imported_scores=imported_scores,
        widget_prefix=widget_prefix,
        precise_input_mode=precise_input_mode,
    )

    person = _build_person_result(profile_name, scores)
    _render_profile_import_export(profile_index, person)

    return person


def _render_multi_profile_inputs(precise_input_mode: bool) -> list[PersonResult]:
    st.header("Profile input")
    st.markdown(
        '<p class="small-muted">Add one or several profiles. Choose slider input or exact numeric input from the sidebar. Each profile can be saved and imported independently.</p>',
        unsafe_allow_html=True,
    )

    profile_count = st.number_input(
        "Number of profiles to compare",
        min_value=1,
        max_value=8,
        value=1,
        step=1,
        help="Use up to 8 profiles to keep the chart readable.",
    )

    people: list[PersonResult] = []

    if int(profile_count) == 1:
        people.append(_render_profile_input(0, precise_input_mode))
        return people

    tabs = st.tabs([f"Profile {index + 1}" for index in range(int(profile_count))])

    for index, tab in enumerate(tabs):
        with tab:
            people.append(_render_profile_input(index, precise_input_mode))

    return people


def _build_export_dataframe(
    people: list[PersonResult],
    personalities,
    filtered_personalities,
    export_mode: str,
    closest_count: int,
) -> pd.DataFrame:
    rows = build_export_rows(
        people=people,
        personalities=personalities,
        mode=export_mode,
        closest_count=closest_count,
        filtered_personalities=filtered_personalities,
    )

    return pd.DataFrame(rows)


def _render_user_guide_tab() -> None:
    st.header("User guide")

    st.markdown(
        """
        Use this workflow to create, compare, save, and export political profiles.
        The app is designed to be used without technical knowledge: start with one profile,
        then add more profiles if you want to compare several people or scenarios.
        """
    )

    step1, step2, step3 = st.columns(3)

    with step1:
        st.subheader("Step 1 - Enter scores")
        st.markdown(
            """
            Choose the number of profiles to compare.

            For each profile, you can either:

            - type exact values with **Manual numeric entry**;
            - disable it and use sliders;
            - paste copied Politiscales-style text and apply detected scores.
            """
        )

    with step2:
        st.subheader("Step 2 - Read the graph")
        st.markdown(
            """
            Open the **Visualization** tab.

            You will see:

            - the profile position on the spectrum;
            - closest reference personalities;
            - a detailed reading based on dominant and weak axes;
            - axis-by-axis balance.
            """
        )

    with step3:
        st.subheader("Step 3 - Save or export")
        st.markdown(
            """
            You can save each profile individually as JSON.

            You can also export the full analysis as CSV for Excel, Power BI,
            or later comparison.
            """
        )

    st.subheader("Recommended workflow")

    st.markdown(
        """
        1. Keep **Manual numeric entry** enabled for precise values.
        2. Enter one profile first and check the result.
        3. Save that profile as JSON if you want to reuse it later.
        4. Increase the number of profiles if you want comparison.
        5. Use filters only when you want reference personalities visible.
        6. Export the CSV when you want a structured analysis file.
        """
    )

    st.subheader("Profile save and import")

    st.markdown(
        """
        Profile saving is currently file-based.

        Each profile can be downloaded as a JSON file and imported again later into any profile form.
        Once imported, the profile remains editable: you can change the name, adjust scores, and save a new version.

        This design prepares the app for a future authenticated version where users can sign in and retrieve
        their saved profiles directly from an account.
        """
    )

    st.subheader("Input mode")

    st.markdown(
        """
        **Manual numeric entry** is enabled by default.

        - Keep it enabled when you want exact score values.
        - Disable it when you prefer visual adjustment with sliders.
        """
    )

    st.subheader("Reference filters")

    st.markdown(
        """
        Reference personalities are hidden by default.

        - `None` hides references for a cleaner graph.
        - `Any` displays references for that filter dimension.
        - A specific value displays only matching references.

        This keeps the graph readable while still allowing deeper comparison when needed.
        """
    )


def _render_methodology_tab() -> None:
    st.header("How the analyzer works")

    st.markdown(
        """
        The analyzer turns 16 ideological scores into a readable political position.
        Each score contributes to one or more interpretive blocks. Those blocks are then compared
        to produce the final economic coordinate `x` and societal coordinate `y`.
        """
    )

    st.subheader("1. Coordinate system")

    st.markdown(
        """
        | Axis | Negative side | Positive side |
        |---|---|---|
        | `x` economic axis | Economic left | Economic right |
        | `y` societal axis | Libertarian / progressive | Authoritarian / conservative |

        Final coordinates are displayed in the range:

        ```text
        x in [-4, 4]
        y in [-4, 4]
        ```

        A profile close to the center has a more balanced or mixed score structure. A profile further
        from the center has a clearer directional tendency.
        """
    )

    st.subheader("2. Score blocks and coefficients")

    st.markdown(
        """
        The model first builds four weighted blocks.

        ### Economic-left block

        ```text
        left_economic =
            0.90 * communisme
          + 0.75 * regulation
          + 0.35 * ecologie
          + 0.25 * revolution
        ```

        Meaning:

        - `communisme` receives the strongest weight because it is the clearest economic-left signal.
        - `regulation` is highly weighted because state intervention directly affects the economic axis.
        - `ecologie` has a moderate effect because ecological priorities often imply economic constraints,
          but ecology is not purely economic.
        - `revolution` has a smaller effect because radicality is a political method, not a direct
          economic position.

        ### Economic-right block

        ```text
        right_economic =
            0.90 * capitalisme
          + 0.75 * laissez_faire
          + 0.35 * productivisme
          + 0.20 * reformisme
        ```

        Meaning:

        - `capitalisme` receives the strongest weight because it is the clearest economic-right signal.
        - `laissez_faire` is highly weighted because it directly expresses deregulation and market autonomy.
        - `productivisme` has a moderate effect because growth and production can exist in several systems,
          but often reinforce a market or expansion-oriented reading.
        - `reformisme` has a smaller effect because gradualism is a method, not a strict right-wing marker.

        ### Libertarian / progressive social block

        ```text
        libertarian_social =
            0.75 * constructivisme
          + 0.70 * justice_rehabilitative
          + 0.70 * progressisme
          + 0.55 * internationalisme
        ```

        Meaning:

        - `constructivisme` strongly contributes to the progressive/libertarian side because it reflects
          flexible social interpretation.
        - `justice_rehabilitative` strongly contributes because it favors reintegration over coercion.
        - `progressisme` strongly contributes because it directly measures openness to social reform.
        - `internationalisme` contributes moderately because it reflects openness beyond national boundaries.

        ### Authoritarian / conservative social block

        ```text
        authoritarian_social =
            0.75 * essentialisme
          + 0.70 * justice_punitive
          + 0.70 * conservatisme
          + 0.55 * nationalisme
        ```

        Meaning:

        - `essentialisme` strongly contributes because it implies stable and fixed social categories.
        - `justice_punitive` strongly contributes because it reinforces order, sanction, and authority.
        - `conservatisme` strongly contributes because it directly measures attachment to continuity.
        - `nationalisme` contributes moderately because it reinforces sovereignty and collective identity.
        """
    )

    st.subheader("3. Raw axis calculation")

    st.markdown(
        """
        Once the four blocks are computed, the model compares opposite forces:

        ```text
        economic_raw = right_economic - left_economic
        societal_raw = authoritarian_social - libertarian_social
        ```

        Therefore:

        - if `economic_raw` is negative, the profile moves left;
        - if `economic_raw` is positive, the profile moves right;
        - if `societal_raw` is negative, the profile moves libertarian/progressive;
        - if `societal_raw` is positive, the profile moves authoritarian/conservative.
        """
    )

    st.subheader("4. Secondary adjustments")

    st.markdown(
        """
        Three smaller corrections refine the result:

        ```text
        economic_raw += 0.12 * (productivisme - ecologie)
        societal_raw += 0.10 * (nationalisme - internationalisme)
        societal_raw += 0.08 * (revolution - reformisme)
        ```

        These are intentionally lower than the main coefficients.

        - `productivisme - ecologie` adjusts the economic reading around growth versus ecological constraint.
        - `nationalisme - internationalisme` adjusts the social reading around national priority versus global openness.
        - `revolution - reformisme` adjusts the authority/posture reading around rupture versus institutional gradualism.
        """
    )

    st.subheader("5. Normalization and final coordinates")

    st.markdown(
        """
        The raw values are normalized:

        ```text
        economic_normalized = economic_raw / 120
        societal_normalized = societal_raw / 120
        ```

        Then they are compressed into the visible graph range:

        ```text
        x = 4 * sigmoid_scaled(economic_normalized)
        y = 4 * sigmoid_scaled(societal_normalized)
        ```

        The sigmoid step keeps the graph readable: very strong scores still move toward the edges,
        but without making the visualization unusable.
        """
    )

    st.subheader("6. Meaning of the 16 axes")

    axes_rows = [
        {"Axis": "constructivisme", "What it means": "Social norms and identities are understood as shaped by history, institutions, and context.", "High score indicates": "A more constructivist and socially fluid interpretation of society."},
        {"Axis": "essentialisme", "What it means": "Identities, cultures, or social roles are seen as more fixed, inherited, or stable.", "High score indicates": "A stronger attachment to stable social categories and inherited structures."},
        {"Axis": "justice_rehabilitative", "What it means": "Justice is seen through reintegration, prevention, and rehabilitation.", "High score indicates": "Preference for restorative justice and reduced purely punitive logic."},
        {"Axis": "justice_punitive", "What it means": "Justice is seen through sanction, deterrence, responsibility, and order.", "High score indicates": "Preference for stronger penalties and stricter law-and-order responses."},
        {"Axis": "progressisme", "What it means": "Support for social reform, modernization, and expansion of rights.", "High score indicates": "A profile open to social change and progressive reforms."},
        {"Axis": "conservatisme", "What it means": "Attachment to continuity, tradition, social stability, and inherited norms.", "High score indicates": "A profile cautious toward rapid social change."},
        {"Axis": "internationalisme", "What it means": "Preference for cross-border cooperation and global or supranational perspectives.", "High score indicates": "A more cosmopolitan or internationally cooperative outlook."},
        {"Axis": "nationalisme", "What it means": "Priority given to sovereignty, national identity, and national interest.", "High score indicates": "A stronger national-priority and sovereignty-oriented outlook."},
        {"Axis": "communisme", "What it means": "Support for collective ownership, redistribution, or anti-capitalist economic logic.", "High score indicates": "A strong movement toward the economic left."},
        {"Axis": "capitalisme", "What it means": "Support for private ownership, markets, entrepreneurship, and capital accumulation.", "High score indicates": "A strong movement toward the economic right."},
        {"Axis": "regulation", "What it means": "Support for rules, public oversight, and institutional control of markets.", "High score indicates": "A preference for regulated markets and public correction of economic imbalances."},
        {"Axis": "laissez_faire", "What it means": "Support for market autonomy and limited state intervention.", "High score indicates": "A preference for deregulation and freer economic activity."},
        {"Axis": "ecologie", "What it means": "Priority given to environmental responsibility and sustainability.", "High score indicates": "A preference for ecological limits and sustainability over unrestricted growth."},
        {"Axis": "productivisme", "What it means": "Priority given to production, infrastructure, growth, and material expansion.", "High score indicates": "A profile more favorable to output, industry, and productive capacity."},
        {"Axis": "revolution", "What it means": "Preference for rupture, systemic transformation, and radical change.", "High score indicates": "A more rupture-oriented political strategy."},
        {"Axis": "reformisme", "What it means": "Preference for gradual change through existing institutions.", "High score indicates": "A more institutional, gradualist, and reform-oriented strategy."},
    ]

    st.dataframe(pd.DataFrame(axes_rows), use_container_width=True, hide_index=True)

    st.subheader("7. How to read your result")

    st.markdown(
        """
        The app gives three levels of reading:

        1. **Graph position** - where the profile appears on the spectrum.
        2. **Closest references** - which reference personalities are geometrically closest.
        3. **Personalized profile reading** - which axes dominate, which axes are weakest, and which
           opposing pairs define the profile most strongly.

        The detailed reading is based on the raw 16 scores, not only on the final `x/y` coordinates.
        """
    )


def main() -> None:
    _inject_css()

    personalities = _load_reference_personalities()

    _render_hero()

    filtered_personalities = _render_reference_filters(personalities)
    export_mode, closest_count, precise_input_mode = _render_sidebar_export_options()

    input_tab, guide_tab, graph_tab, data_tab, methodology_tab = st.tabs(
        ["Input", "Guide", "Visualization", "Reference data", "Methodology"]
    )

    with input_tab:
        people = _render_multi_profile_inputs(precise_input_mode)

    with guide_tab:
        _render_user_guide_tab()

    with graph_tab:
        st.header("Political positioning")

        fig = build_political_spectrum_figure(
            people=people,
            personalities=filtered_personalities,
        )

        st.plotly_chart(fig, use_container_width=True)

        _render_analysis(people, personalities)

        export_df = _build_export_dataframe(
            people=people,
            personalities=personalities,
            filtered_personalities=filtered_personalities,
            export_mode=export_mode,
            closest_count=closest_count,
        )

        csv_content = export_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="Download analysis CSV",
            data=csv_content,
            file_name="political_spectrum_analysis.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with data_tab:
        st.header("Reference dataset")

        data = [
            {
                "Name": person.name,
                "Group": person.display_group,
                "Country": person.country,
                "Period": person.period,
                "Ideology family": person.ideology_family,
                "x": person.x,
                "y": person.y,
                "Confidence": person.confidence,
                "Notes": person.notes,
            }
            for person in personalities
        ]

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    with methodology_tab:
        _render_methodology_tab()


if __name__ == "__main__":
    main()