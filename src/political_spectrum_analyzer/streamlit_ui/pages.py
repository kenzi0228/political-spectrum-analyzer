"""Page renderers for the Streamlit app."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import streamlit as st

from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.services.export_results_service import build_export_rows
from political_spectrum_analyzer.streamlit_ui.analysis_rendering import render_analysis
from political_spectrum_analyzer.web.plotly_plot import build_political_spectrum_figure


Translate = Callable[[str, str], str]


def render_sidebar_export_options(language: str, translate: Translate) -> tuple[str, int]:
    st.sidebar.markdown(f"### {translate(language, 'export_options')}")
    export_mode = st.sidebar.selectbox(
        translate(language, "csv_export_mode"),
        [
            "profiles_only",
            "closest_references",
            "all_references",
            "filtered_references",
        ],
        format_func=lambda value: {
            "profiles_only": translate(language, "export_profiles_only"),
            "closest_references": translate(language, "export_closest_references"),
            "all_references": translate(language, "export_all_references"),
            "filtered_references": translate(language, "export_filtered_references"),
        }[value],
    )

    closest_count = st.sidebar.number_input(
        translate(language, "closest_references_count"),
        min_value=1,
        max_value=20,
        value=3,
        step=1,
    )

    return str(export_mode), int(closest_count)


def build_export_dataframe(
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


def render_visualization_page(
    people: list[PersonResult],
    personalities,
    filtered_personalities,
    language: str,
    translate: Translate,
) -> None:
    st.header(translate(language, "political_positioning_header"))

    export_mode, closest_count = render_sidebar_export_options(language, translate)

    fig = build_political_spectrum_figure(
        people=people,
        personalities=filtered_personalities,
    )

    st.plotly_chart(fig, use_container_width=True)

    render_analysis(people, filtered_personalities, language)

    export_df = build_export_dataframe(
        people=people,
        personalities=personalities,
        filtered_personalities=filtered_personalities,
        export_mode=export_mode,
        closest_count=closest_count,
    )

    csv_content = export_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label=translate(language, "download_analysis_csv"),
        data=csv_content,
        file_name="political_spectrum_analysis.csv",
        mime="text/csv",
        use_container_width=True,
    )


def render_reference_data_page(filtered_personalities, language: str, translate: Translate) -> None:
    st.header(translate(language, "reference_dataset_header"))

    data = [
        {
            translate(language, "table_name"): person.name,
            translate(language, "table_group"): person.display_group,
            translate(language, "table_country"): person.country,
            translate(language, "table_period"): person.period,
            translate(language, "table_ideology_family"): person.ideology_family,
            translate(language, "table_role_category"): getattr(person, "role_category", ""),
            translate(language, "table_gender"): getattr(person, "gender", ""),
            translate(language, "table_country_codes"): getattr(person, "country_codes", ""),
            translate(language, "table_century"): getattr(person, "century", ""),
            "x": person.x,
            "y": person.y,
            translate(language, "table_confidence"): person.confidence,
            translate(language, "table_notes"): person.notes,
        }
        for person in filtered_personalities
    ]

    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
