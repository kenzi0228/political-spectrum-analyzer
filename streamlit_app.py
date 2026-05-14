from __future__ import annotations

import pandas as pd
import streamlit as st

from political_spectrum_analyzer.config import PERSONALITIES_CSV_PATH
from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.model.transforms import apply_transformations_and_get_coordinates
from political_spectrum_analyzer.services.analysis_service import analyze_profile
from political_spectrum_analyzer.services.export_results_service import build_export_rows
from political_spectrum_analyzer.services.personalities_service import load_personalities
from political_spectrum_analyzer.services.personality_filter_service import (
    ANY_VALUE,
    NONE_VALUE,
    filter_personalities,
    get_unique_values,
)
from political_spectrum_analyzer.services.text_import_service import extract_scores_from_text
from political_spectrum_analyzer.web.plotly_plot import build_political_spectrum_figure


st.set_page_config(
    page_title="Political Spectrum Analyzer",
    page_icon="ðŸ“Š",
    layout="wide",
)


def _format_variable_name(variable_name: str) -> str:
    return variable_name.replace("_", " ").capitalize()


@st.cache_data
def _load_reference_personalities():
    return load_personalities(PERSONALITIES_CSV_PATH)


def _default_scores() -> dict[str, int]:
    return {variable: 0 for variable in VARIABLE_NAMES}


def _build_person_result(profile_name: str, scores: dict[str, int]) -> PersonResult:
    x, y = apply_transformations_and_get_coordinates(scores)

    return PersonResult(
        name=profile_name.strip() or "Profile",
        scores=scores,
        x=float(x),
        y=float(y),
    )


def _render_analysis(person: PersonResult, personalities) -> None:
    analysis = analyze_profile(person=person, personalities=personalities, top_n=3)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("x coordinate", f"{analysis.x:.3f}")
    col2.metric("y coordinate", f"{analysis.y:.3f}")
    col3.metric("Quadrant", analysis.quadrant)
    col4.metric("Distance to center", f"{analysis.distance_to_center:.3f}")

    st.subheader("Closest references")

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


def _render_reference_filters(personalities):
    st.sidebar.subheader("Reference filters")

    group = st.sidebar.selectbox(
        "Group",
        get_unique_values(personalities, "display_group"),
        index=0,
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

    st.sidebar.caption(
        f"Displayed references: {len(filtered)} / {len(personalities)}"
    )

    if group == NONE_VALUE and country == NONE_VALUE and period == NONE_VALUE and ideology == NONE_VALUE:
        st.sidebar.info("Set one filter to Any or to a specific value to display references.")

    return filtered, {
        "group": group,
        "country": country,
        "period": period,
        "ideology": ideology,
    }


def _render_score_inputs(imported_scores: dict[str, int] | None) -> dict[str, int]:
    scores = imported_scores or _default_scores()

    cols = st.columns(2)
    output_scores: dict[str, int] = {}

    for index, variable in enumerate(VARIABLE_NAMES):
        with cols[index % 2]:
            output_scores[variable] = st.slider(
                _format_variable_name(variable),
                min_value=0,
                max_value=100,
                value=int(scores.get(variable, 0)),
                step=1,
            )

    return output_scores


def _build_export_dataframe(
    person: PersonResult,
    personalities,
    filtered_personalities,
    export_mode: str,
    closest_count: int,
) -> pd.DataFrame:
    rows = build_export_rows(
        people=[person],
        personalities=personalities,
        mode=export_mode,
        closest_count=closest_count,
        filtered_personalities=filtered_personalities,
    )

    return pd.DataFrame(rows)


def main() -> None:
    personalities = _load_reference_personalities()

    st.title("Political Spectrum Analyzer")
    st.caption(
        "Interactive web version of the desktop app: political positioning, reference comparison, text import, filters, and CSV export."
    )

    st.warning(
        "This application uses an explainable heuristic model. Reference positions are approximate and should not be interpreted as objective political classifications.",
        icon="âš ï¸",
    )

    filtered_personalities, active_filters = _render_reference_filters(personalities)

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

    input_tab, graph_tab, data_tab, methodology_tab = st.tabs(
        ["Input", "Visualization", "Reference data", "Methodology"]
    )

    imported_scores = None

    with input_tab:
        st.header("Profile input")

        profile_name = st.text_input("Profile name", value="My profile")

        with st.expander("Import from copied Politiscales-style text", expanded=False):
            copied_text = st.text_area(
                "Paste copied results text",
                height=220,
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

        scores = _render_score_inputs(imported_scores)

    person = _build_person_result(profile_name, scores)

    with graph_tab:
        st.header("Political positioning")

        fig = build_political_spectrum_figure(
            people=[person],
            personalities=filtered_personalities,
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Position analysis")
        _render_analysis(person, personalities)

        export_df = _build_export_dataframe(
            person=person,
            personalities=personalities,
            filtered_personalities=filtered_personalities,
            export_mode=export_mode,
            closest_count=int(closest_count),
        )

        csv_content = export_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            label="Download analysis CSV",
            data=csv_content,
            file_name="political_spectrum_analysis.csv",
            mime="text/csv",
        )

    with data_tab:
        st.header("Reference dataset")

        data = [
            {
                "name": person.name,
                "group": person.display_group,
                "country": person.country,
                "period": person.period,
                "ideology_family": person.ideology_family,
                "x": person.x,
                "y": person.y,
                "confidence": person.confidence,
                "notes": person.notes,
            }
            for person in personalities
        ]

        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    with methodology_tab:
        st.header("Methodology summary")

        st.markdown(
            """
            The application projects 16 ideological scores into a two-dimensional space.

            - `x < 0`: economic left
            - `x > 0`: economic right
            - `y < 0`: libertarian / progressive
            - `y > 0`: authoritarian / conservative

            The projection is heuristic and explainable. It is intended for exploration and visualization, not for definitive political classification.

            Reference personalities are estimated anchors with uncertainty and confidence metadata. Closest references are computed with Euclidean distance in the 2D space.
            """
        )

        st.markdown("See `docs/methodology.md` and `docs/reference_dataset.md` for the full documentation.")


if __name__ == "__main__":
    main()