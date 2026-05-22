from __future__ import annotations
import re
# Reference chart tooltip contract: display_group is descriptive hover metadata, while role_category is the user-facing filter dimension.
# Role category is the user-facing reference filter.
REFERENCE_TOOLTIP_FIELDS = ['name', 'display_group', 'role_category', 'ideology_family', 'ideology_subtype']


import sys
from pathlib import Path

PACKAGE_SRC_PATH = Path(__file__).resolve().parent / "src"
if PACKAGE_SRC_PATH.exists() and str(PACKAGE_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC_PATH))

import pandas as pd
import streamlit as st

from political_spectrum_analyzer.config import PERSONALITIES_CSV_PATH
from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.services.export_results_service import build_export_rows
from political_spectrum_analyzer.services.personalities_service import load_personalities
from political_spectrum_analyzer.services.advanced_profile_interpretation_service import build_advanced_interpretation_rows, build_advanced_profile_interpretation
from political_spectrum_analyzer.services.profile_comparison_service import build_comparison_rows, build_profile_comparisons
from political_spectrum_analyzer.services.advanced_profile_comparison_service import build_advanced_comparison_rows, build_advanced_profile_comparisons, build_similarity_matrix
from political_spectrum_analyzer.services.personality_filter_service import (

    NONE_VALUE,
    filter_personalities,
    get_unique_values,
)
from political_spectrum_analyzer.streamlit_ui.analysis_rendering import (
    render_analysis as _render_analysis,
)
from political_spectrum_analyzer.streamlit_ui.content_pages import (
    render_about_tab,
    render_hero,
    render_user_guide_tab,
)
from political_spectrum_analyzer.streamlit_ui.navigation import (
    render_active_view_selector as _render_active_view_selector,
    render_inactive_view_notice as _render_inactive_view_notice,
    view_requires_reference_dataset as _view_requires_reference_dataset,
)
from political_spectrum_analyzer.streamlit_ui.profile_inputs import (
    render_multi_profile_inputs as _render_multi_profile_inputs,
)
from political_spectrum_analyzer.streamlit_ui.methodology import (
    render_methodology_v3 as _render_methodology_v3,
)
from political_spectrum_analyzer.streamlit_ui.profile_state import (
    build_people_from_state as _build_people_from_state,
)
from political_spectrum_analyzer.streamlit_ui.reference_filters import (
    render_reference_multiselect_filters as _render_reference_multiselect_filters,
)
from political_spectrum_analyzer.streamlit_ui.styles import (
    force_dark_metric_cards as _force_dark_metric_cards,
    force_dark_sidebar as _force_dark_sidebar,
    inject_css as _inject_css,
)
from political_spectrum_analyzer.streamlit_ui.text import (
    markdown_text as _md_text,
    translate as _t,
)
from political_spectrum_analyzer.web.plotly_plot import build_political_spectrum_figure

try:
    import plotly.express as px
except Exception:  # pragma: no cover - Plotly is optional at import time.
    px = None


st.set_page_config(
    page_title="Political Spectrum Analyzer",
    page_icon=":bar_chart:",
    layout="wide",
)



@st.cache_data
def _load_reference_personalities():
    return load_personalities(PERSONALITIES_CSV_PATH)


def _render_hero(language: str) -> None:
    render_hero(language, _t)


def _render_reference_filters(personalities):
    current_language = st.session_state.get("language", "en")
    st.sidebar.header(_t(current_language, "sidebar_controls"))
    st.sidebar.selectbox(
        _t(current_language, "language_label"),
        options=["en", "fr"],
        format_func=lambda value: "English" if value == "en" else "Francais",
        key="language",
    )
    st.sidebar.subheader(_t(current_language, "reference_filters_sidebar"))

    role_category = st.sidebar.selectbox(
        _t(current_language, "table_role_category"),
        get_unique_values(personalities, "role_category"),
        index=0,
        help=_t(current_language, "reference_filters_body"),
    )

    country = st.sidebar.selectbox(
        _t(current_language, "table_country"),
        get_unique_values(personalities, "country"),
        index=0,
    )

    period = st.sidebar.selectbox(
        _t(current_language, "table_period"),
        get_unique_values(personalities, "period"),
        index=0,
    )

    ideology = st.sidebar.selectbox(
        _t(current_language, "table_ideology_family"),
        get_unique_values(personalities, "ideology_family"),
        index=0,
    )

    filtered = filter_personalities(
        personalities=personalities,
        role_category=role_category,
        country=country,
        period=period,
        ideology_family=ideology,
    )

    st.sidebar.metric(
        _t(current_language, "reference_dataset_header"),
        f"{len(filtered)} / {len(personalities)}",
    )

    if role_category == NONE_VALUE and country == NONE_VALUE and period == NONE_VALUE and ideology == NONE_VALUE:
        st.sidebar.info(_t(current_language, "reference_filters_body"))

    return filtered


def _render_sidebar_input_mode() -> bool:
    precise_input_mode = st.sidebar.toggle(
        _t(st.session_state.get("language", "en"), "manual_numeric_entry"),
        value=True,
        help=_t(st.session_state.get("language", "en"), "manual_numeric_help"),
    )

    return bool(precise_input_mode)


def _render_sidebar_export_options(language: str):
    st.sidebar.subheader(_t(language, "export_options"))

    export_mode = st.sidebar.selectbox(
        _t(language, "csv_export_mode"),
        [
            "profiles_only",
            "closest_references",
            "all_references",
            "filtered_references",
        ],
        format_func=lambda value: {
            "profiles_only": _t(language, "export_profiles_only"),
            "closest_references": _t(language, "export_closest_references"),
            "all_references": _t(language, "export_all_references"),
            "filtered_references": _t(language, "export_filtered_references"),
        }[value],
    )

    closest_count = st.sidebar.number_input(
        _t(language, "closest_references_count"),
        min_value=1,
        max_value=20,
        value=3,
        step=1,
    )

    return export_mode, int(closest_count)


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


def _render_user_guide_tab(language: str) -> None:
    render_user_guide_tab(language, _t, _md_text)


def _render_advanced_profile_interpretations(people: list, language: str) -> None:
    st.subheader(_t(language, "advanced_interpretation_header"))
    st.markdown(_t(language, "advanced_interpretation_intro"))

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

            st.markdown(f"**{_t(language, 'advanced_interpretation_dominant')}**")
            st.dataframe(pd.DataFrame([axis.__dict__ for axis in interpretation.dominant_axes]), use_container_width=True, hide_index=True)

            st.markdown(f"**{_t(language, 'advanced_interpretation_weak')}**")
            st.dataframe(pd.DataFrame([axis.__dict__ for axis in interpretation.weak_axes]), use_container_width=True, hide_index=True)

            st.markdown(f"**{_t(language, 'advanced_interpretation_secondary')}**")
            st.dataframe(
                pd.DataFrame([{"dimension": key, "value": value} for key, value in interpretation.secondary_dimensions.items()]),
                use_container_width=True,
                hide_index=True,
            )

    st.markdown(f"**{_t(language, 'advanced_interpretation_table')}**")
    st.dataframe(pd.DataFrame(build_advanced_interpretation_rows(interpretations)), use_container_width=True, hide_index=True)


def _render_advanced_profile_comparisons(people: list, language: str) -> None:
    st.subheader(_t(language, "advanced_comparison_header"))
    st.markdown(_t(language, "advanced_comparison_intro"))

    comparisons = build_advanced_profile_comparisons(people)

    if not comparisons:
        st.info(_t(language, "advanced_comparison_not_enough"))
        return

    st.markdown(f"**{_t(language, 'advanced_comparison_matrix')}**")
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

            st.markdown(f"**{_t(language, 'advanced_comparison_gaps')}**")

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

    st.markdown(f"**{_t(language, 'advanced_comparison_table')}**")
    st.dataframe(
        pd.DataFrame(build_advanced_comparison_rows(comparisons)),
        use_container_width=True,
        hide_index=True,
    )


def _render_profile_comparison_analysis(people, language: str) -> None:
    st.subheader(_t(language, "profile_comparison_header"))
    st.markdown(_t(language, "profile_comparison_intro"))

    comparisons = build_profile_comparisons(people)

    if not comparisons:
        st.info(_t(language, "profile_comparison_not_enough"))
        return

    for comparison in comparisons:
        with st.expander(f"{comparison.first_name} vs {comparison.second_name}", expanded=False):
            metric_col_1, metric_col_2 = st.columns(2)
            metric_col_1.metric("Distance", f"{comparison.coordinate_distance:.2f}")
            metric_col_2.metric("Similarity", f"{comparison.ideological_similarity_score:.1f}/100")

            st.markdown(f"**{_t(language, 'profile_comparison_summary')}**")
            st.write(comparison.summary)

            if comparison.shared_strong_axes:
                st.caption(
                    _t(language, "profile_comparison_shared_dominant").format(
                        axes=", ".join(comparison.shared_strong_axes)
                    )
                )

            if comparison.shared_weak_axes:
                st.caption(
                    _t(language, "profile_comparison_shared_weak").format(
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

    st.markdown(f"**{_t(language, 'profile_comparison_table')}**")
    st.dataframe(pd.DataFrame(build_comparison_rows(comparisons)), use_container_width=True, hide_index=True)


def _render_about_tab(language: str) -> None:
    render_about_tab(language, _t, _md_text)


def _render_methodology_tab(language: str) -> None:
    st.header(_t(language, "methodology_header"))

    st.markdown(_t(language, "methodology_intro"))

    st.subheader(_t(language, "coordinate_system"))

    st.markdown(
        """
        | Axis | Negative side | Positive side |
        |---|---|---|
        | `x` economic axis | Economic left | Economic right |
        | `y` societal axis | Libertarian / progressive | Authoritarian / conservative |

        ```text
        x in [-4, 4]
        y in [-4, 4]
        ```
        """
    )

    st.subheader(_t(language, "score_blocks"))

    st.markdown(_md_text(language, "formula_main_blocks_intro"))
    st.info(_md_text(language, "formula_coefficients_note"))

    st.markdown(f"### {_t(language, 'formula_left_block_title')}")
    st.code(
        "left_economic =\\n"
        "    0.95 * communisme\\n"
        "  + 0.75 * regulation\\n"
        "  + 0.28 * ecologie\\n"
        "  + revolution excluded from coordinate blocks",
        language="text",
    )
    st.markdown(_md_text(language, "formula_left_block_explanation"))

    st.markdown(f"### {_t(language, 'formula_right_block_title')}")
    st.code(
        "right_economic =\\n"
        "    0.95 * capitalisme\\n"
        "  + 0.80 * laissez_faire\\n"
        "  + 0.24 * productivisme\\n"
        "  + reformisme excluded from coordinate blocks",
        language="text",
    )
    st.markdown(_md_text(language, "formula_right_block_explanation"))

    st.markdown(f"### {_t(language, 'formula_libertarian_block_title')}")
    st.code(
        "libertarian_social =\\n"
        "    0.75 * constructivisme\\n"
        "  + 0.70 * justice_rehabilitative\\n"
        "  + 0.75 * progressisme\\n"
        "  + 0.35 * internationalisme",
        language="text",
    )
    st.markdown(_md_text(language, "formula_libertarian_block_explanation"))

    st.markdown(f"### {_t(language, 'formula_authoritarian_block_title')}")
    st.code(
        "authoritarian_social =\\n"
        "    0.60 * essentialisme\\n"
        "  + 0.70 * justice_punitive\\n"
        "  + 0.70 * conservatisme\\n"
        "  + 0.30 * nationalisme",
        language="text",
    )
    st.markdown(_md_text(language, "formula_authoritarian_block_explanation"))

    st.subheader(_t(language, "raw_axis"))

    st.code(
        "economic_raw = right_economic - left_economic\\n"
        "societal_raw = authoritarian_social - libertarian_social",
        language="text",
    )
    st.markdown(_md_text(language, "formula_raw_axis_explanation"))

    st.subheader(_t(language, "secondary_adjustments"))

    st.code(
        "economic_raw += 0.04 * (productivisme - ecologie)\\n"
        "societal_raw += 0.03 * (nationalisme - internationalisme)\\n"
        "revolution and reformisme excluded from coordinate normalization",
        language="text",
    )
    st.markdown(_md_text(language, "formula_adjustments_explanation"))

    st.subheader(_t(language, "normalization"))

    st.code(
        "x = 4 * tanh(0.015 * economic_raw)\\n"
        "y = 4 * tanh(0.015 * societal_raw)",
        language="text",
    )
    st.markdown(_md_text(language, "formula_normalization_explanation"))

    st.subheader(_t(language, "axes_meaning"))

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

    st.subheader(_t(language, "read_result"))

    st.markdown(
        """
        The app gives three levels of reading:

        1. **Graph position** - where the profile appears on the spectrum.
        2. **Closest references** - which reference personalities are geometrically closest.
        3. **Personalized profile reading** - which axes dominate, which axes are weakest, and which opposing pairs define the profile most strongly.

        The detailed reading is based on the raw 16 scores, not only on the final `x/y` coordinates.
        """
    )


def _profile_value(profile, field_name: str, default=None):
    if isinstance(profile, dict):
        return profile.get(field_name, default)
    return getattr(profile, field_name, default)


def _profile_scores_for_v3(profile) -> dict:
    """Extract secondary scores from a profile-like object for interpretation v3."""
    if isinstance(profile, dict):
        scores = profile.get("scores", {})
        if isinstance(scores, dict):
            return scores
        return {
            key: value
            for key, value in profile.items()
            if key not in {"name", "x", "y"}
        }

    scores = getattr(profile, "scores", None)
    if isinstance(scores, dict):
        return scores

    output = {}
    for key in [
        "ecologie",
        "ecology",
        "productivisme",
        "productivism",
        "internationalisme",
        "internationalism",
        "nationalisme",
        "nationalism",
        "revolution",
        "reformisme",
        "reformism",
    ]:
        if hasattr(profile, key):
            output[key] = getattr(profile, key)

    return output


def _render_integrated_analysis_v3(people: list, reference_people: list, language: str) -> None:
    """Render the actually used analysis block with v3 non-repetitive output."""
    if not people:
        st.info("Add at least one profile to generate an analysis.")
        return

    st.subheader("Personalized analysis")

    for index, person in enumerate(people, start=1):
        name = str(_profile_value(person, "name", f"Profile {index}") or f"Profile {index}")
        x = float(_profile_value(person, "x", 0.0) or 0.0)
        y = float(_profile_value(person, "y", 0.0) or 0.0)
        secondary_scores = _profile_scores_for_v3(person)

        st.markdown(f"#### {name}")
        render_advanced_profile_interpretation_v3(
            x=x,
            y=y,
            secondary_scores=secondary_scores,
            nearest_profiles=[],
        )

    if len(people) >= 2:
        st.subheader("Profile comparison")
        first = people[0]
        second = people[1]

        render_advanced_profile_comparison_v3(
            profile_a={
                "x": _profile_value(first, "x", 0.0),
                "y": _profile_value(first, "y", 0.0),
            },
            profile_b={
                "x": _profile_value(second, "x", 0.0),
                "y": _profile_value(second, "y", 0.0),
            },
            secondary_a=_profile_scores_for_v3(first),
            secondary_b=_profile_scores_for_v3(second),
        )


def main() -> None:
    _inject_css()
    _force_dark_sidebar()
    _force_dark_metric_cards()

    language = st.session_state.get("language", "en")

    _render_hero(language)

    st.sidebar.header(_t(language, "sidebar_controls"))
    current_language = st.session_state.get("language", "en")
    st.sidebar.selectbox(
        _t(current_language, "language_label"),
        options=["en", "fr"],
        format_func=lambda value: "English" if value == "en" else "Francais",
        key="language",
    )
    active_view = _render_active_view_selector(language, _t)

    st.sidebar.markdown(f"### {_t(language, 'score_input_mode_header')}")
    st.sidebar.caption(_t(language, "score_input_mode_caption"))
    precise_input_mode = _render_sidebar_input_mode()

    personalities = []
    filtered_personalities = []

    if _view_requires_reference_dataset(active_view):
        personalities = _load_reference_personalities()
        filtered_personalities = _render_reference_multiselect_filters(personalities, language)
    else:
        st.sidebar.caption(_t(language, "reference_dataset_not_loaded"))

    input_tab, guide_tab, graph_tab, data_tab, methodology_tab = st.tabs(
        [_t(language, "tab_input"), _t(language, "tab_guide"), _t(language, "tab_visualization"), _t(language, "tab_reference"), _t(language, "tab_methodology")]
    )

    with input_tab:
        if active_view == "input":
            people = _render_multi_profile_inputs(precise_input_mode, _t)
        else:
            people = _build_people_from_state()
            _render_inactive_view_notice(_t(language, "tab_input"), language, _t)

    with guide_tab:
        if active_view == "guide":
            _render_user_guide_tab(language)
        else:
            _render_inactive_view_notice(_t(language, "tab_guide"), language, _t)
    with graph_tab:
        if active_view == "visualization":
            st.header(_t(language, "political_positioning_header"))

            export_mode, closest_count = _render_sidebar_export_options(language)

            fig = build_political_spectrum_figure(
                people=people,
                personalities=filtered_personalities,
            )

            st.plotly_chart(fig, use_container_width=True)

            _render_analysis(people, filtered_personalities, language)

            export_df = _build_export_dataframe(
                people=people,
                personalities=personalities,
                filtered_personalities=filtered_personalities,
                export_mode=export_mode,
                closest_count=closest_count,
            )

            csv_content = export_df.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                label=_t(language, "download_analysis_csv"),
                data=csv_content,
                file_name="political_spectrum_analysis.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            _render_inactive_view_notice(_t(language, "tab_visualization"), language, _t)

    with data_tab:
        if active_view == "reference":
            st.header(_t(language, "reference_dataset_header"))

            data = [
                {
                    _t(language, "table_name"): person.name,
                    _t(language, "table_group"): person.display_group,
                    _t(language, "table_country"): person.country,
                    _t(language, "table_period"): person.period,
                    _t(language, "table_ideology_family"): person.ideology_family,
                    _t(language, "table_role_category"): getattr(person, "role_category", ""),
                    _t(language, "table_gender"): getattr(person, "gender", ""),
                    _t(language, "table_country_codes"): getattr(person, "country_codes", ""),
                    _t(language, "table_century"): getattr(person, "century", ""),
                    "x": person.x,
                    "y": person.y,
                    _t(language, "table_confidence"): person.confidence,
                    _t(language, "table_notes"): person.notes,
                }
                for person in filtered_personalities
            ]

            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        else:
            _render_inactive_view_notice(_t(language, "tab_reference"), language, _t)

    with methodology_tab:
        if active_view == "methodology":
            _render_methodology_v3(language)
        else:
            _render_inactive_view_notice(_t(language, "tab_methodology"), language, _t)
    about_tab = locals().get("about_tab", locals().get("guide_tab", locals().get("home_tab", st.container())))
    with about_tab:
        if active_view == "guide":
            _render_about_tab(language)
# Profile comparison analysis is available through _render_profile_comparison_analysis(people_results, language).


# Intended Streamlit render call: _render_advanced_profile_interpretations(people_results, language)

# Intended Streamlit render call: _render_advanced_profile_comparisons(people_results, language)

# Reference multi-select filters are available through _render_reference_multiselect_filters(reference_personalities_for_filters, language).


STREAMLIT_THEME_CSS = """
<style>
/* Base compatibility CSS contract.
   Runtime styling is generated by apply_professional_streamlit_theme(theme_mode). */
.psa-hero {
    border-radius: 24px;
}
</style>
"""

THEME_MODE_LABEL = "Interface theme"
THEME_MODE_HELP = "Switch between a dark interface and a light interface. This only changes visual comfort, not the analysis."
GENDER_FILTER_LABEL = "Gender filter"
GENDER_FILTER_HELP = "Optional metadata filter for the reference profiles. Gender is never used for scoring or ideological interpretation."
SCORE_INPUT_MODE_LABEL = "Score input mode"
SCORE_INPUT_MODE_HELP = "Choose whether scores are entered with sliders or with numeric fields. Sliders are easier for manual exploration; numeric fields are better for precise input."


def render_theme_mode_selector() -> str:
    """Render a sidebar theme selector and return the selected mode."""
    if not hasattr(st, "sidebar"):
        return "Dark"
    return st.sidebar.select_slider(
        THEME_MODE_LABEL,
        options=["Dark", "Light"],
        value=st.session_state.get("theme_mode", "Dark"),
        help=THEME_MODE_HELP,
        key="theme_mode",
    )


def _theme_palette(theme_mode: str) -> dict[str, str]:
    if str(theme_mode).lower() == "light":
        return {
            "app_bg": "#F5F7FB",
            "sidebar_bg": "#FFFFFF",
            "surface": "#FFFFFF",
            "surface_2": "#EEF2FF",
            "text": "#111827",
            "muted": "#4B5563",
            "border": "rgba(17, 24, 39, 0.12)",
            "metric_bg": "rgba(255, 255, 255, 0.94)",
            "hero_bg": "linear-gradient(135deg, rgba(255,255,255,0.98), rgba(238,242,255,0.96))",
            "blue_card": "rgba(108, 99, 255, 0.10)",
            "blue_text": "#3730A3",
            "green_card": "rgba(16, 185, 129, 0.14)",
            "green_text": "#047857",
        }
    return {
        "app_bg": "#0E1117",
        "sidebar_bg": "#111522",
        "surface": "#1A1D2E",
        "surface_2": "#151827",
        "text": "#FAFAFA",
        "muted": "#B8BCCB",
        "border": "rgba(255, 255, 255, 0.10)",
        "metric_bg": "rgba(26, 29, 46, 0.82)",
        "hero_bg": "radial-gradient(circle at top left, rgba(108,99,255,0.28), transparent 34%), linear-gradient(135deg, rgba(26,29,46,0.98), rgba(14,17,23,0.96))",
        "blue_card": "rgba(30, 64, 175, 0.30)",
        "blue_text": "#60A5FA",
        "green_card": "rgba(22, 101, 52, 0.48)",
        "green_text": "#4ADE80",
    }


def apply_professional_streamlit_theme(theme_mode: str = "Dark") -> None:
    """Apply the project's custom Streamlit visual layer."""
    palette = _theme_palette(theme_mode)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {palette["app_bg"]};
            color: {palette["text"]};
        }}
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }}
        [data-testid="stSidebar"] {{
            background: {palette["sidebar_bg"]} !important;
            border-right: 1px solid {palette["border"]};
        }}
        [data-testid="stSidebar"] * {{
            color: {palette["text"]} !important;
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div,
        [data-testid="stSidebar"] [data-baseweb="base-input"],
        [data-testid="stSidebar"] input {{
            background: {palette["surface_2"]} !important;
            color: {palette["text"]} !important;
            border-color: {palette["border"]} !important;
            border-radius: 12px !important;
        }}
        [data-testid="stSidebar"] [data-testid="stMetric"] {{
            background: {palette["metric_bg"]} !important;
            color: {palette["text"]} !important;
            border: 1px solid {palette["border"]};
        }}
        div[data-testid="stMetric"] {{
            background: {palette["metric_bg"]};
            border: 1px solid {palette["border"]};
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.14);
        }}
        div[data-testid="stTabs"] button {{
            border-radius: 999px;
            padding-left: 1rem;
            padding-right: 1rem;
        }}
        div[data-testid="stTabs"] button[aria-selected="true"] {{
            background: rgba(108, 99, 255, 0.22);
            color: {palette["text"]};
        }}
        .stButton > button,
        .stDownloadButton > button {{
            border-radius: 999px;
            border: 1px solid rgba(108, 99, 255, 0.42);
            background: linear-gradient(135deg, rgba(108, 99, 255, 0.98), rgba(121, 86, 255, 0.78));
            color: #FAFAFA;
            font-weight: 650;
            box-shadow: 0 10px 26px rgba(108, 99, 255, 0.24);
        }}
        div[data-testid="stExpander"] {{
            border: 1px solid {palette["border"]};
            border-radius: 18px;
            background: {palette["surface"]};
        }}
        .psa-hero {{
            padding: 1.25rem 1.4rem;
            border-radius: 24px;
            background: {palette["hero_bg"]};
            border: 1px solid rgba(108, 99, 255, 0.22);
            box-shadow: 0 18px 46px rgba(0, 0, 0, 0.18);
            margin-bottom: 1.2rem;
        }}
        .psa-hero h1 {{
            margin: 0;
            font-size: 2.25rem;
            line-height: 1.05;
            color: {palette["text"]};
        }}
        .psa-hero p {{
            color: {palette["muted"]};
            margin-top: 0.65rem;
            margin-bottom: 0;
            font-size: 1.02rem;
        }}
        .psa-info-card {{
            background: {palette["blue_card"]};
            color: {palette["blue_text"]};
            border-radius: 14px;
            padding: 1rem;
            border: 1px solid {palette["border"]};
        }}
        .psa-success-card {{
            background: {palette["green_card"]};
            color: {palette["green_text"]};
            border-radius: 14px;
            padding: 1rem;
            border: 1px solid {palette["border"]};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_streamlit_hero(title: str, subtitle: str) -> None:
    """Render a compact hero block used by the Streamlit app."""
    st.markdown(
        f"""
        <div class="psa-hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_gender_filter_selector(available_genders=None) -> list[str]:
    """Render an optional gender filter for reference-profile exploration."""
    normalized = []
    for value in available_genders or ["male", "female"]:
        value = str(value).strip().lower()
        if value and value not in normalized:
            normalized.append(value)
    if not normalized:
        normalized = ["male", "female"]
    selected = st.sidebar.multiselect(
        GENDER_FILTER_LABEL,
        options=normalized,
        default=[],
        help=GENDER_FILTER_HELP,
        key="reference_gender_filter",
    )
    st.session_state["reference_gender_filter_values"] = selected
    return selected


def filter_reference_dataframe_by_gender(dataframe, selected_genders):
    """Apply the optional gender filter to a pandas dataframe."""
    if dataframe is None or not selected_genders or "gender" not in dataframe.columns:
        return dataframe
    wanted = {str(value).strip().lower() for value in selected_genders if str(value).strip()}
    if not wanted:
        return dataframe
    return dataframe[dataframe["gender"].astype(str).str.lower().isin(wanted)]


def filter_reference_rows_by_gender(rows, selected_genders):
    """Apply the optional gender filter to a list of dictionaries."""
    if not selected_genders:
        return rows
    wanted = {str(value).strip().lower() for value in selected_genders if str(value).strip()}
    if not wanted:
        return rows
    return [row for row in rows if str(row.get("gender", "")).strip().lower() in wanted]


def deduplicate_profile_reading_sentences(text: str) -> str:
    """Remove repeated sentences from generated profile-reading text."""
    if not text:
        return text
    parts = re.split(r"(?<=[.!?])\\s+", str(text).strip())
    seen = set()
    output = []
    for part in parts:
        normalized = re.sub(r"\\s+", " ", part).strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        output.append(part.strip())
    return " ".join(output)


def render_score_input_mode_selector() -> str:
    """Render the score-input mode selector with an explicit label and help text."""
    return st.sidebar.select_slider(
        SCORE_INPUT_MODE_LABEL,
        options=["Sliders", "Numeric fields"],
        value=st.session_state.get("score_input_mode", "Sliders"),
        help=SCORE_INPUT_MODE_HELP,
        key="score_input_mode",
    )


PLOTLY_REFERENCE_TOOLTIP_FIELDS = [
    "name",
    "display_group",
    "role_category",
    "gender",
    "country",
    "country_codes",
    "period",
    "ideology_family",
    "ideology_subtype",
    "confidence",
    "notes",
]


def build_reference_plotly_figure(reference_data):
    """Build an interactive Plotly reference-map figure when Plotly is available."""
    if px is None:
        return None
    dataframe = pd.DataFrame(reference_data)
    if dataframe.empty or not {"x", "y", "name"}.issubset(dataframe.columns):
        return None
    dataframe = dataframe.copy()
    dataframe["x"] = pd.to_numeric(dataframe["x"], errors="coerce")
    dataframe["y"] = pd.to_numeric(dataframe["y"], errors="coerce")
    dataframe = dataframe.dropna(subset=["x", "y"])
    if dataframe.empty:
        return None
    color_column = "ideology_family" if "ideology_family" in dataframe.columns else None
    hover_columns = [column for column in PLOTLY_REFERENCE_TOOLTIP_FIELDS if column in dataframe.columns]
    figure = px.scatter(
        dataframe,
        x="x",
        y="y",
        color=color_column,
        hover_name="name",
        hover_data=hover_columns,
        template="plotly_dark",
        height=720,
    )
    figure.update_traces(
        marker={
            "size": 9,
            "opacity": 0.82,
            "line": {"width": 0.7, "color": "rgba(255,255,255,0.42)"},
        }
    )
    figure.update_layout(
        title="Interactive reference map",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font={"color": "#FAFAFA"},
        legend_title_text="Ideology family",
        margin={"l": 42, "r": 28, "t": 68, "b": 42},
        xaxis={
            "title": "Economic axis: left â† 0 â†’ right",
            "range": [-4.2, 4.2],
            "zeroline": True,
            "zerolinewidth": 1,
            "zerolinecolor": "rgba(250,250,250,0.35)",
            "gridcolor": "rgba(250,250,250,0.08)",
        },
        yaxis={
            "title": "Social axis: libertarian â† 0 â†’ authoritarian",
            "range": [-4.2, 4.2],
            "zeroline": True,
            "zerolinewidth": 1,
            "zerolinecolor": "rgba(250,250,250,0.35)",
            "gridcolor": "rgba(250,250,250,0.08)",
        },
    )
    figure.add_hline(y=0, line_width=1, line_color="rgba(250,250,250,0.35)")
    figure.add_vline(x=0, line_width=1, line_color="rgba(250,250,250,0.35)")
    return figure


def render_reference_plotly_chart(reference_data) -> bool:
    """Render the interactive reference map and return whether Plotly was used."""
    figure = build_reference_plotly_figure(reference_data)
    if figure is None:
        return False
    st.plotly_chart(figure, use_container_width=True, config={"displaylogo": False})
    return True


DEFAULT_REFERENCE_RENDERER = "plotly"

REFERENCE_MULTISELECT_FILTER_FIELDS = {
    "ideology_family": "Ideology family",
    "role_category": "Role category",
    "gender": "Gender",
    "century": "Century",
    "confidence": "Confidence",
}


def _split_reference_filter_values(value) -> list[str]:
    """Split scalar or semi-colon separated reference metadata values."""
    if value is None:
        return []

    raw = str(value).replace(",", ";")
    return [item.strip() for item in raw.split(";") if item.strip()]


def _unique_reference_filter_options(reference_rows, field: str) -> list[str]:
    """Collect sorted unique options for one reference metadata field."""
    values = set()

    if reference_rows is None:
        return []

    if hasattr(reference_rows, "to_dict"):
        iterable = reference_rows.to_dict("records")
    else:
        iterable = reference_rows

    for row in iterable:
        if not isinstance(row, dict):
            continue

        for value in _split_reference_filter_values(row.get(field, "")):
            values.add(value)

    return sorted(values, key=lambda item: item.lower())


def render_reference_multiselect_filters(reference_rows) -> dict[str, list[str]]:
    """Render every reference filter as a multi-select widget."""
    selected_filters: dict[str, list[str]] = {}

    for field, label in REFERENCE_MULTISELECT_FILTER_FIELDS.items():
        options = _unique_reference_filter_options(reference_rows, field)

        selected_filters[field] = st.sidebar.multiselect(
            label,
            options=options,
            default=[],
            help=(
                "Optional multi-select filter. Leave empty to keep all values "
                f"for {label.lower()}."
            ),
            key=f"reference_multiselect_{field}",
        )

    st.session_state["reference_multiselect_filters"] = selected_filters
    return selected_filters


def _row_matches_multiselect_filter(row: dict, field: str, selected_values: list[str]) -> bool:
    if not selected_values:
        return True

    wanted = {str(value).strip().lower() for value in selected_values if str(value).strip()}
    if not wanted:
        return True

    row_values = {
        value.lower()
        for value in _split_reference_filter_values(row.get(field, ""))
    }

    return bool(row_values & wanted)


def apply_reference_multiselect_filters(reference_rows, selected_filters: dict[str, list[str]]):
    """Apply all reference multi-select filters to rows or a dataframe."""
    if reference_rows is None or not selected_filters:
        return reference_rows

    is_dataframe = hasattr(reference_rows, "to_dict")
    rows = reference_rows.to_dict("records") if is_dataframe else list(reference_rows)

    filtered_rows = [
        row for row in rows
        if all(
            _row_matches_multiselect_filter(row, field, selected_values)
            for field, selected_values in selected_filters.items()
        )
    ]

    if is_dataframe:
        return pd.DataFrame(filtered_rows, columns=reference_rows.columns)

    return filtered_rows


def render_reference_filters_and_apply(reference_rows):
    """Render all reference filters as multi-select widgets and return filtered rows."""
    selected_filters = render_reference_multiselect_filters(reference_rows)
    return apply_reference_multiselect_filters(reference_rows, selected_filters)


def render_default_reference_map(reference_rows) -> str:
    """Render the reference map with Plotly first, then fall back to legacy rendering."""
    if render_reference_plotly_chart(reference_rows):
        return "plotly"

    st.info(
        "Interactive Plotly rendering is unavailable in this environment. "
        "The app kept the reference data available through the legacy view."
    )
    return "fallback"


ADVANCED_INTERPRETATION_V3_VERSION = "v3"

INTERPRETATION_V3_DIMENSION_LABELS = {
    "economic": "economic orientation",
    "social": "social authority orientation",
    "international": "international orientation",
    "ecology": "ecology / productivism",
    "revolution": "change strategy",
}


def _interpretation_v3_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _interpretation_v3_band(value: float) -> str:
    absolute = abs(value)

    if absolute >= 3.2:
        return "very strong"
    if absolute >= 2.2:
        return "strong"
    if absolute >= 1.2:
        return "moderate"
    if absolute >= 0.45:
        return "light"
    return "balanced"


def _interpretation_v3_axis_label(axis: str, value: float) -> str:
    if axis == "x":
        if value < -0.45:
            return "economically left"
        if value > 0.45:
            return "economically right"
        return "economically mixed"

    if axis == "y":
        if value < -0.45:
            return "socially libertarian"
        if value > 0.45:
            return "socially authoritarian"
        return "socially mixed"

    return "mixed"


def _interpretation_v3_quadrant(x: float, y: float) -> str:
    if x < -0.45 and y < -0.45:
        return "left-libertarian"
    if x < -0.45 and y > 0.45:
        return "left-authoritarian"
    if x > 0.45 and y < -0.45:
        return "right-libertarian"
    if x > 0.45 and y > 0.45:
        return "right-authoritarian"
    return "hybrid / centrist"


def _interpretation_v3_tension_sentences(x: float, y: float, secondary_scores: dict | None = None) -> list[str]:
    secondary_scores = secondary_scores or {}
    sentences: list[str] = []

    ecology = _interpretation_v3_float(
        secondary_scores.get("ecology", secondary_scores.get("ecologie", secondary_scores.get("environment", 0.0)))
    )
    productivism = _interpretation_v3_float(
        secondary_scores.get("productivism", secondary_scores.get("productivisme", 0.0))
    )
    internationalism = _interpretation_v3_float(
        secondary_scores.get("internationalism", secondary_scores.get("internationalisme", 0.0))
    )
    nationalism = _interpretation_v3_float(
        secondary_scores.get("nationalism", secondary_scores.get("nationalisme", 0.0))
    )
    revolution = _interpretation_v3_float(
        secondary_scores.get("revolution", secondary_scores.get("revolutionary", 0.0))
    )
    reformism = _interpretation_v3_float(
        secondary_scores.get("reformism", secondary_scores.get("reformisme", 0.0))
    )

    if x < -1.2 and y > 1.2:
        sentences.append(
            "Your profile combines economic interventionism with a stronger preference for order, hierarchy, or collective discipline."
        )
    elif x > 1.2 and y < -1.2:
        sentences.append(
            "Your profile combines market-oriented economics with a strong preference for individual autonomy and civil liberties."
        )
    elif x < -1.2 and y < -1.2:
        sentences.append(
            "Your profile is coherent around egalitarian economics, social openness, and resistance to concentrated authority."
        )
    elif x > 1.2 and y > 1.2:
        sentences.append(
            "Your profile is coherent around market-oriented economics, social order, and institutional authority."
        )
    else:
        sentences.append(
            "Your profile is mixed enough that the most important information is found in the secondary dimensions rather than in a single quadrant label."
        )

    if ecology - productivism >= 1.0:
        sentences.append(
            "Ecology appears as a real structuring dimension: environmental limits probably matter more to you than pure growth or productivity."
        )
    elif productivism - ecology >= 1.0:
        sentences.append(
            "Productivism appears stronger than ecological restraint: you probably give high priority to infrastructure, growth, output, or technological capacity."
        )

    if internationalism - nationalism >= 1.0:
        sentences.append(
            "Your internationalist tendency suggests openness to cross-border cooperation, universalist norms, or reduced emphasis on national sovereignty."
        )
    elif nationalism - internationalism >= 1.0:
        sentences.append(
            "Your nationalist tendency suggests stronger attachment to sovereignty, borders, national cohesion, or strategic autonomy."
        )

    if revolution - reformism >= 1.0:
        sentences.append(
            "Your change strategy is more rupture-oriented: you are likely less satisfied with gradual institutional reform when core structures are seen as defective."
        )
    elif reformism - revolution >= 1.0:
        sentences.append(
            "Your change strategy is more reformist: you likely prefer institutional correction, legal continuity, and gradual transformation."
        )

    return sentences


def deduplicate_interpretation_sentences(text: str) -> str:
    """Remove repeated sentences and repeated adjacent interpretation fragments."""
    if not text:
        return text

    parts = re.split(r"(?<=[.!?])\s+", str(text).strip())
    seen = set()
    output: list[str] = []

    for part in parts:
        normalized = re.sub(r"\s+", " ", part).strip().lower()
        normalized = normalized.replace("**", "").replace("__", "")

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        output.append(part.strip())

    return " ".join(output)


def build_advanced_profile_interpretation_v3(
    x: float,
    y: float,
    secondary_scores: dict | None = None,
    nearest_profiles: list[dict] | None = None,
) -> dict[str, object]:
    """Build a richer, non-repetitive personalized interpretation payload."""
    x = _interpretation_v3_float(x)
    y = _interpretation_v3_float(y)
    secondary_scores = secondary_scores or {}
    nearest_profiles = nearest_profiles or []

    economic_label = _interpretation_v3_axis_label("x", x)
    social_label = _interpretation_v3_axis_label("y", y)
    quadrant = _interpretation_v3_quadrant(x, y)

    summary = (
        f"Your position is best described as {quadrant}: "
        f"{_interpretation_v3_band(x)} {economic_label} and "
        f"{_interpretation_v3_band(y)} {social_label}."
    )

    analysis_parts = [
        summary,
        *(_interpretation_v3_tension_sentences(x, y, secondary_scores)),
    ]

    if nearest_profiles:
        names = [
            str(profile.get("name", "")).strip()
            for profile in nearest_profiles[:3]
            if str(profile.get("name", "")).strip()
        ]
        if names:
            analysis_parts.append(
                "The closest reference profiles should be read as analytical neighbors, not as exact ideological equivalents: "
                + ", ".join(names)
                + "."
            )

    analysis = deduplicate_interpretation_sentences(" ".join(analysis_parts))

    return {
        "version": ADVANCED_INTERPRETATION_V3_VERSION,
        "quadrant": quadrant,
        "economic_label": economic_label,
        "social_label": social_label,
        "summary": summary,
        "analysis": analysis,
        "secondary_dimensions_used": sorted(secondary_scores.keys()),
    }


def render_advanced_profile_interpretation_v3(
    x: float,
    y: float,
    secondary_scores: dict | None = None,
    nearest_profiles: list[dict] | None = None,
) -> dict[str, object]:
    """Render advanced interpretation v3 and return the payload for tests/export."""
    payload = build_advanced_profile_interpretation_v3(
        x=x,
        y=y,
        secondary_scores=secondary_scores,
        nearest_profiles=nearest_profiles,
    )

    st.markdown("### Advanced personalized interpretation v3")
    st.write(payload["analysis"])

    return payload


ADVANCED_COMPARISON_V3_VERSION = "v3"

COMPARISON_V3_AXIS_LABELS = {
    "x": "economic axis",
    "y": "social-authority axis",
    "ecology": "ecology / productivism",
    "internationalism": "internationalism / nationalism",
    "reformism": "reformism / rupture",
}


def _comparison_v3_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _comparison_v3_gap_band(value: float) -> str:
    absolute = abs(value)

    if absolute >= 3.0:
        return "very large"
    if absolute >= 2.0:
        return "large"
    if absolute >= 1.0:
        return "moderate"
    if absolute >= 0.35:
        return "small"
    return "minimal"


def _comparison_v3_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def _comparison_v3_compatibility_score(distance: float) -> int:
    # Coordinates live roughly in [-4, 4]. Max diagonal is about 11.31.
    normalized = max(0.0, min(1.0, 1.0 - (distance / 8.0)))
    return round(normalized * 100)


def _comparison_v3_axis_sentence(axis: str, gap: float) -> str:
    band = _comparison_v3_gap_band(gap)

    if axis == "x":
        if abs(gap) < 0.35:
            return "Both profiles are very close on the economic axis."
        if gap > 0:
            return f"Profile B is more economically right-wing than Profile A; the gap is {band}."
        return f"Profile B is more economically left-wing than Profile A; the gap is {band}."

    if axis == "y":
        if abs(gap) < 0.35:
            return "Both profiles are very close on the social-authority axis."
        if gap > 0:
            return f"Profile B is more authoritarian or order-oriented than Profile A; the gap is {band}."
        return f"Profile B is more libertarian or autonomy-oriented than Profile A; the gap is {band}."

    return f"The gap on {COMPARISON_V3_AXIS_LABELS.get(axis, axis)} is {band}."


def _comparison_v3_secondary_gap_sentences(
    secondary_a: dict | None,
    secondary_b: dict | None,
) -> list[str]:
    secondary_a = secondary_a or {}
    secondary_b = secondary_b or {}
    sentences: list[str] = []

    pairs = [
        ("ecology", "productivism", "ecology / productivism"),
        ("internationalism", "nationalism", "internationalism / nationalism"),
        ("reformism", "revolution", "reformism / rupture"),
    ]

    for positive_key, negative_key, label in pairs:
        a_score = _comparison_v3_float(secondary_a.get(positive_key, 0.0)) - _comparison_v3_float(secondary_a.get(negative_key, 0.0))
        b_score = _comparison_v3_float(secondary_b.get(positive_key, 0.0)) - _comparison_v3_float(secondary_b.get(negative_key, 0.0))
        gap = b_score - a_score

        if abs(gap) < 0.75:
            continue

        direction = "stronger" if gap > 0 else "weaker"
        sentences.append(
            f"On {label}, Profile B is {direction} than Profile A; this adds a secondary nuance beyond the main x/y coordinates."
        )

    return sentences


def _comparison_v3_ranked_gaps(x_gap: float, y_gap: float, secondary_a: dict | None, secondary_b: dict | None) -> list[dict[str, object]]:
    secondary_a = secondary_a or {}
    secondary_b = secondary_b or {}

    gaps = [
        {"axis": "x", "label": "economic axis", "gap": x_gap, "absolute_gap": abs(x_gap)},
        {"axis": "y", "label": "social-authority axis", "gap": y_gap, "absolute_gap": abs(y_gap)},
    ]

    for key in sorted(set(secondary_a) | set(secondary_b)):
        a_value = _comparison_v3_float(secondary_a.get(key, 0.0))
        b_value = _comparison_v3_float(secondary_b.get(key, 0.0))
        gap = b_value - a_value
        if abs(gap) >= 0.35:
            gaps.append(
                {
                    "axis": key,
                    "label": key.replace("_", " "),
                    "gap": gap,
                    "absolute_gap": abs(gap),
                }
            )

    return sorted(gaps, key=lambda item: item["absolute_gap"], reverse=True)


def deduplicate_comparison_sentences(text: str) -> str:
    """Remove repeated sentences from comparison text."""
    if not text:
        return text

    parts = re.split(r"(?<=[.!?])\s+", str(text).strip())
    seen = set()
    output: list[str] = []

    for part in parts:
        normalized = re.sub(r"\s+", " ", part).strip().lower()
        normalized = normalized.replace("**", "").replace("__", "")

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        output.append(part.strip())

    return " ".join(output)


def build_advanced_profile_comparison_v3(
    profile_a: dict,
    profile_b: dict,
    secondary_a: dict | None = None,
    secondary_b: dict | None = None,
) -> dict[str, object]:
    """Build a richer comparison between two ideological profiles."""
    x_a = _comparison_v3_float(profile_a.get("x", 0.0))
    y_a = _comparison_v3_float(profile_a.get("y", 0.0))
    x_b = _comparison_v3_float(profile_b.get("x", 0.0))
    y_b = _comparison_v3_float(profile_b.get("y", 0.0))

    x_gap = x_b - x_a
    y_gap = y_b - y_a
    distance = _comparison_v3_distance(x_a, y_a, x_b, y_b)
    compatibility = _comparison_v3_compatibility_score(distance)

    ranked_gaps = _comparison_v3_ranked_gaps(x_gap, y_gap, secondary_a, secondary_b)

    convergence_sentences = []
    divergence_sentences = [
        _comparison_v3_axis_sentence("x", x_gap),
        _comparison_v3_axis_sentence("y", y_gap),
        *(_comparison_v3_secondary_gap_sentences(secondary_a, secondary_b)),
    ]

    if abs(x_gap) < 0.35:
        convergence_sentences.append("The two profiles converge economically.")
    if abs(y_gap) < 0.35:
        convergence_sentences.append("The two profiles converge on the social-authority axis.")

    if not convergence_sentences:
        convergence_sentences.append("The two profiles do not strongly converge on the two main axes.")

    summary = (
        f"The ideological distance between the two profiles is {distance:.2f}, "
        f"with an estimated compatibility score of {compatibility}/100."
    )

    comparison_text = deduplicate_comparison_sentences(
        " ".join([summary, *convergence_sentences, *divergence_sentences])
    )

    return {
        "version": ADVANCED_COMPARISON_V3_VERSION,
        "distance": round(distance, 3),
        "compatibility_score": compatibility,
        "x_gap": round(x_gap, 3),
        "y_gap": round(y_gap, 3),
        "ranked_gaps": ranked_gaps,
        "summary": summary,
        "comparison": comparison_text,
    }


def render_advanced_profile_comparison_v3(
    profile_a: dict,
    profile_b: dict,
    secondary_a: dict | None = None,
    secondary_b: dict | None = None,
) -> dict[str, object]:
    """Render comparison v3 and return its payload for export/tests."""
    payload = build_advanced_profile_comparison_v3(
        profile_a=profile_a,
        profile_b=profile_b,
        secondary_a=secondary_a,
        secondary_b=secondary_b,
    )

    st.markdown("### Advanced profile comparison v3")
    st.metric("Ideological distance", f"{payload['distance']:.2f}")
    st.metric("Compatibility score", f"{payload['compatibility_score']}/100")
    st.write(payload["comparison"])

    return payload

if __name__ == "__main__":
    main()

