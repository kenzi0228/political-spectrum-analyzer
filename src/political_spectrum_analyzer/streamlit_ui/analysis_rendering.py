"""Detailed profile analysis rendering for the Streamlit app."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.services.analysis_service import analyze_profile
from political_spectrum_analyzer.services.profile_interpretation_service import interpret_profile
from political_spectrum_analyzer.streamlit_ui.text import translate


def render_single_profile_analysis(person: PersonResult, personalities, language: str = "en") -> None:
    analysis = analyze_profile(person=person, personalities=personalities, top_n=3)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(translate(language, "metric_x_coordinate"), f"{analysis.x:.3f}")
    col2.metric(translate(language, "metric_y_coordinate"), f"{analysis.y:.3f}")
    col3.metric(translate(language, "metric_quadrant"), analysis.quadrant)
    col4.metric(translate(language, "metric_distance_to_center"), f"{analysis.distance_to_center:.3f}")

    closest_data = [
        {
            translate(language, "table_rank"): index,
            translate(language, "table_name"): match.name,
            translate(language, "table_group"): match.display_group,
            translate(language, "table_distance"): match.distance,
            "x": match.x,
            "y": match.y,
        }
        for index, match in enumerate(analysis.closest_references, start=1)
    ]

    st.dataframe(pd.DataFrame(closest_data), use_container_width=True, hide_index=True)
    render_profile_interpretation(person, language)


def render_profile_interpretation(person: PersonResult, language: str = "en") -> None:
    interpretation = interpret_profile(
        profile_name=person.name,
        scores=person.scores,
    )

    st.markdown(f"#### {translate(language, 'analysis_personalized_reading')}")
    st.success(interpretation.archetype)
    st.write(interpretation.synthesis)

    diagnostic_cols = st.columns(3)
    diagnostic_cols[0].metric(
        translate(language, "analysis_intensity_score"),
        f"{interpretation.intensity_score:.1f}/100",
    )
    diagnostic_cols[1].metric(
        translate(language, "analysis_coherence_score"),
        f"{interpretation.coherence_score:.1f}/100",
    )
    diagnostic_cols[2].metric(
        translate(language, "analysis_center_of_gravity"),
        interpretation.center_of_gravity,
    )

    if interpretation.diagnostic_notes:
        st.markdown(f"#### {translate(language, 'analysis_diagnostic_notes')}")
        for note in interpretation.diagnostic_notes:
            st.markdown(f"- {note}")

    reading_details = [
        (translate(language, "analysis_economic_reading"), interpretation.economic_reading),
        (translate(language, "analysis_societal_reading"), interpretation.societal_reading),
        (translate(language, "analysis_strategic_reading"), interpretation.strategic_reading),
        (translate(language, "analysis_internal_tension"), interpretation.tension_reading),
    ]

    synthesis_normalized = " ".join(str(interpretation.synthesis).lower().split())
    unique_reading_details = []
    seen_reading_details = set()

    for label, text in reading_details:
        text = str(text).strip()
        normalized = " ".join(text.lower().split())

        if not normalized:
            continue
        if normalized in seen_reading_details:
            continue
        if normalized in synthesis_normalized:
            continue

        seen_reading_details.add(normalized)
        unique_reading_details.append((label, text))

    if unique_reading_details:
        st.markdown(f"#### {translate(language, 'analysis_detailed_notes')}")
        for label, text in unique_reading_details:
            st.markdown(f"- **{label}:** {text}")

    if interpretation.profile_highlights:
        st.markdown(f"#### {translate(language, 'analysis_highlights')}")
        for highlight in interpretation.profile_highlights:
            st.markdown(f"- {highlight}")

    dominant_rows = [
        {
            translate(language, "table_axis"): axis.label,
            translate(language, "table_score"): axis.score,
            translate(language, "table_level"): axis.level,
            translate(language, "table_meaning"): axis.interpretation,
        }
        for axis in interpretation.dominant_axes
    ]

    weak_rows = [
        {
            translate(language, "table_axis"): axis.label,
            translate(language, "table_score"): axis.score,
            translate(language, "table_level"): axis.level,
            translate(language, "table_meaning"): axis.interpretation,
        }
        for axis in interpretation.weak_axes
    ]

    balance_rows = [
        {
            translate(language, "table_dimension"): row["dimension"],
            translate(language, "table_first_pole"): row["left_axis"],
            translate(language, "table_first_score"): row["left_score"],
            translate(language, "table_second_pole"): row["right_axis"],
            translate(language, "table_second_score"): row["right_score"],
            translate(language, "table_leading_tendency"): row["leading_side"],
            translate(language, "table_reading"): row["reading"],
        }
        for row in interpretation.axis_pair_balances
    ]

    score_note_rows = [
        {
            translate(language, "table_axis"): axis.label,
            translate(language, "table_score"): axis.score,
            translate(language, "table_level"): axis.level,
            translate(language, "table_reading"): axis.interpretation,
        }
        for axis in interpretation.score_notes
    ]

    st.markdown(f"#### {translate(language, 'analysis_dominant_axes')}")
    st.dataframe(pd.DataFrame(dominant_rows), use_container_width=True, hide_index=True)

    st.markdown(f"#### {translate(language, 'analysis_weakest_axes')}")
    st.dataframe(pd.DataFrame(weak_rows), use_container_width=True, hide_index=True)

    st.markdown(f"#### {translate(language, 'analysis_axis_balance')}")
    st.dataframe(pd.DataFrame(balance_rows), use_container_width=True, hide_index=True)

    st.markdown(f"#### {translate(language, 'analysis_score_by_score')}")
    st.dataframe(pd.DataFrame(score_note_rows), use_container_width=True, hide_index=True)


def render_analysis(people: list[PersonResult], personalities, language: str = "en") -> None:
    if not people:
        st.info(translate(language, "analysis_no_profile"))
        return

    if len(people) == 1:
        st.subheader(translate(language, "analysis_single_header").format(name=people[0].name))
        render_single_profile_analysis(people[0], personalities, language)
        return

    st.subheader(translate(language, "analysis_multi_header"))

    summary_rows = []
    for person in people:
        analysis = analyze_profile(person=person, personalities=personalities, top_n=3)
        interpretation = interpret_profile(profile_name=person.name, scores=person.scores)

        closest = analysis.closest_references[0].name if analysis.closest_references else ""

        summary_rows.append(
            {
                translate(language, "table_profile"): analysis.name,
                translate(language, "table_profile_type"): interpretation.archetype,
                "x": analysis.x,
                "y": analysis.y,
                translate(language, "metric_quadrant"): analysis.quadrant,
                translate(language, "metric_distance_to_center"): analysis.distance_to_center,
                translate(language, "table_closest_reference"): closest,
            }
        )

    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    st.markdown(f"### {translate(language, 'analysis_details_by_profile')}")
    for person in people:
        with st.expander(person.name, expanded=False):
            render_single_profile_analysis(person, personalities, language)
