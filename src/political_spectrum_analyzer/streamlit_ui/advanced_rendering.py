"""Advanced interpretation and comparison renderers for Streamlit."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import streamlit as st

from political_spectrum_analyzer.services.advanced_profile_comparison_service import (
    build_advanced_comparison_rows,
    build_advanced_profile_comparisons,
    build_similarity_matrix,
)
from political_spectrum_analyzer.services.advanced_profile_interpretation_service import (
    build_advanced_interpretation_rows,
    build_advanced_profile_interpretation,
)
from political_spectrum_analyzer.services.profile_comparison_service import (
    build_comparison_rows,
    build_profile_comparisons,
)


Translate = Callable[[str, str], str]


def render_advanced_profile_interpretations(people: list, language: str, translate: Translate) -> None:
    st.subheader(translate(language, "advanced_interpretation_header"))
    st.markdown(translate(language, "advanced_interpretation_intro"))

    interpretations = [
        build_advanced_profile_interpretation(person.name, person.scores, person.x, person.y)
        for person in people
    ]

    for interpretation in interpretations:
        with st.expander(interpretation.profile_name, expanded=False):
            st.write(interpretation.short_summary)
            st.markdown(interpretation.detailed_summary)

            metric_cols = st.columns(4)
            metric_cols[0].metric("Coherence", f"{interpretation.coherence_score:.1f}/100")
            metric_cols[1].metric("Intensity", f"{interpretation.intensity_score:.1f}/100")
            metric_cols[2].metric("Moderation", f"{interpretation.moderation_score:.1f}/100")
            metric_cols[3].metric("Radicality", f"{interpretation.radicality_score:.1f}/100")

            st.markdown(f"**{translate(language, 'advanced_interpretation_dominant')}**")
            st.dataframe(pd.DataFrame([axis.__dict__ for axis in interpretation.dominant_axes]), use_container_width=True, hide_index=True)

            st.markdown(f"**{translate(language, 'advanced_interpretation_weak')}**")
            st.dataframe(pd.DataFrame([axis.__dict__ for axis in interpretation.weak_axes]), use_container_width=True, hide_index=True)

            st.markdown(f"**{translate(language, 'advanced_interpretation_secondary')}**")
            st.dataframe(
                pd.DataFrame([{"dimension": key, "value": value} for key, value in interpretation.secondary_dimensions.items()]),
                use_container_width=True,
                hide_index=True,
            )

    st.markdown(f"**{translate(language, 'advanced_interpretation_table')}**")
    st.dataframe(pd.DataFrame(build_advanced_interpretation_rows(interpretations)), use_container_width=True, hide_index=True)


def render_advanced_profile_comparisons(people: list, language: str, translate: Translate) -> None:
    st.subheader(translate(language, "advanced_comparison_header"))
    st.markdown(translate(language, "advanced_comparison_intro"))

    comparisons = build_advanced_profile_comparisons(people)

    if not comparisons:
        st.info(translate(language, "advanced_comparison_not_enough"))
        return

    st.markdown(f"**{translate(language, 'advanced_comparison_matrix')}**")
    st.dataframe(
        pd.DataFrame(build_similarity_matrix(people)),
        use_container_width=True,
        hide_index=True,
    )

    for comparison in comparisons:
        with st.expander(f"{comparison.first_name} vs {comparison.second_name}", expanded=False):
            metric_cols = st.columns(4)
            metric_cols[0].metric("Global", f"{comparison.global_similarity_score:.1f}/100")
            metric_cols[1].metric("Economic", f"{comparison.economic_similarity_score:.1f}/100")
            metric_cols[2].metric("Societal", f"{comparison.societal_similarity_score:.1f}/100")
            metric_cols[3].metric("Secondary", f"{comparison.secondary_similarity_score:.1f}/100")

            st.write(comparison.summary)
            st.caption(comparison.detailed_summary)

            st.markdown(f"**{translate(language, 'advanced_comparison_gaps')}**")

            axis_gap_rows = [
                {
                    "axis": gap.axis,
                    "first_score": gap.first_score,
                    "second_score": gap.second_score,
                    "absolute_gap": gap.absolute_gap,
                }
                for gap in comparison.largest_axis_gaps
            ]
            st.dataframe(pd.DataFrame(axis_gap_rows), use_container_width=True, hide_index=True)

            secondary_gap_rows = [
                {
                    "dimension": gap.dimension,
                    "first_value": gap.first_value,
                    "second_value": gap.second_value,
                    "absolute_gap": gap.absolute_gap,
                }
                for gap in comparison.secondary_dimension_gaps
            ]
            st.dataframe(pd.DataFrame(secondary_gap_rows), use_container_width=True, hide_index=True)

    st.markdown(f"**{translate(language, 'advanced_comparison_table')}**")
    st.dataframe(
        pd.DataFrame(build_advanced_comparison_rows(comparisons)),
        use_container_width=True,
        hide_index=True,
    )


def render_profile_comparison_analysis(people, language: str, translate: Translate) -> None:
    st.subheader(translate(language, "profile_comparison_header"))
    st.markdown(translate(language, "profile_comparison_intro"))

    comparisons = build_profile_comparisons(people)

    if not comparisons:
        st.info(translate(language, "profile_comparison_not_enough"))
        return

    for comparison in comparisons:
        with st.expander(f"{comparison.first_name} vs {comparison.second_name}", expanded=False):
            metric_col_1, metric_col_2 = st.columns(2)
            metric_col_1.metric("Distance", f"{comparison.coordinate_distance:.2f}")
            metric_col_2.metric("Similarity", f"{comparison.ideological_similarity_score:.1f}/100")

            st.markdown(f"**{translate(language, 'profile_comparison_summary')}**")
            st.write(comparison.summary)

            if comparison.shared_strong_axes:
                st.caption(
                    translate(language, "profile_comparison_shared_dominant").format(
                        axes=", ".join(comparison.shared_strong_axes)
                    )
                )

            if comparison.shared_weak_axes:
                st.caption(
                    translate(language, "profile_comparison_shared_weak").format(
                        axes=", ".join(comparison.shared_weak_axes)
                    )
                )

            gap_rows = [
                {
                    "axis": gap.axis,
                    "first_score": gap.first_score,
                    "second_score": gap.second_score,
                    "absolute_gap": gap.absolute_gap,
                }
                for gap in comparison.largest_score_gaps
            ]

            st.dataframe(pd.DataFrame(gap_rows), use_container_width=True, hide_index=True)

    st.markdown(f"**{translate(language, 'profile_comparison_table')}**")
    st.dataframe(pd.DataFrame(build_comparison_rows(comparisons)), use_container_width=True, hide_index=True)
