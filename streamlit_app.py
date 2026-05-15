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
    NONE_VALUE,
    filter_personalities,
    get_unique_values,
)
from political_spectrum_analyzer.services.text_import_service import extract_scores_from_text
from political_spectrum_analyzer.web.plotly_plot import build_political_spectrum_figure


st.set_page_config(
    page_title="Political Spectrum Analyzer",
    page_icon="ÃƒÂ°Ã…Â¸Ã¢â‚¬Å“Ã…Â ",
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
    border-left: 4px solid #f59e0b;
    background: #fffbeb;
    color: #78350f;
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

section[data-testid="stSidebar"] {
    background-color: #f8fafc;
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


def _build_person_result(profile_name: str, scores: dict[str, int]) -> PersonResult:
    x, y = apply_transformations_and_get_coordinates(scores)

    return PersonResult(
        name=profile_name.strip() or "Profile",
        scores=scores,
        x=float(x),
        y=float(y),
    )


def _render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Political Spectrum Analyzer</div>
            <div class="hero-subtitle">
                Interactive web version of the desktop application for ideological score projection,
                multi-profile comparison, reference comparison, nearest-neighbor analysis, and CSV export.
            </div>
            <div style="margin-top: 0.9rem;">
                <span class="feature-pill">Python</span>
                <span class="feature-pill">Streamlit</span>
                <span class="feature-pill">Plotly</span>
                <span class="feature-pill">Multi-profile comparison</span>
                <span class="feature-pill">CSV export</span>
                <span class="feature-pill">150 reference profiles</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="warning-box">
            This tool uses an explainable heuristic model. Reference positions are approximate and should
            not be interpreted as objective political classifications.
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


def _render_analysis(people: list[PersonResult], personalities) -> None:
    if not people:
        st.info("No profile available for analysis.")
        return

    if len(people) == 1:
        st.subheader(f"Analysis ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â {people[0].name}")
        _render_single_profile_analysis(people[0], personalities)
        return

    st.subheader("Multi-profile analysis")

    summary_rows = []
    for person in people:
        analysis = analyze_profile(person=person, personalities=personalities, top_n=3)

        closest = analysis.closest_references[0].name if analysis.closest_references else ""

        summary_rows.append(
            {
                "Profile": analysis.name,
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

    return export_mode, int(closest_count)


def _render_score_inputs(
    imported_scores: dict[str, int] | None,
    widget_prefix: str,
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
                with cols[index % 2]:
                    output_scores[variable] = st.slider(
                        _format_variable_name(variable),
                        min_value=0,
                        max_value=100,
                        value=int(scores.get(variable, 0)),
                        step=1,
                        key=f"{widget_prefix}_{variable}",
                    )

    for variable in VARIABLE_NAMES:
        output_scores.setdefault(variable, int(scores.get(variable, 0)))

    return output_scores


def _render_profile_input(profile_index: int) -> PersonResult:
    widget_prefix = f"profile_{profile_index}"

    st.markdown(f"### Profile {profile_index + 1}")

    profile_name = st.text_input(
        "Profile name",
        value=f"Profile {profile_index + 1}",
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

    scores = _render_score_inputs(
        imported_scores=imported_scores,
        widget_prefix=widget_prefix,
    )

    return _build_person_result(profile_name, scores)


def _render_multi_profile_inputs() -> list[PersonResult]:
    st.header("Profile input")
    st.markdown(
        '<p class="small-muted">Add one or several profiles. Each profile can be entered manually or imported from copied Politiscales-style text. OCR is intentionally excluded from the web version for deployment reliability.</p>',
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
        people.append(_render_profile_input(0))
        return people

    tabs = st.tabs([f"Profile {index + 1}" for index in range(int(profile_count))])

    for index, tab in enumerate(tabs):
        with tab:
            people.append(_render_profile_input(index))

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


def _render_methodology_tab() -> None:
    st.header("Methodology")

    st.markdown(
        """
        This application transforms 16 ideological scores into a 2D political position.

        The goal is not to produce an absolute political truth. The model is an explainable heuristic:
        every score contributes to an interpretable economic or societal direction, then the final
        position is projected onto a readable map.
        """
    )

    st.subheader("1. Coordinate system")

    st.markdown(
        """
        The graph uses two axes:

        | Axis | Negative side | Positive side |
        |---|---|---|
        | `x` economic axis | Economic left | Economic right |
        | `y` societal axis | Libertarian / progressive | Authoritarian / conservative |

        The final coordinates are bounded inside:

        ```text
        x in [-4, 4]
        y in [-4, 4]
        ```

        Interpretation:

        - `x < 0`: more economically left;
        - `x > 0`: more economically right;
        - `y < 0`: more libertarian / socially progressive;
        - `y > 0`: more authoritarian / socially conservative.
        """
    )

    st.subheader("2. Calculation formula")

    st.markdown(
        """
        The model first computes four intermediate blocks:

        ```text
        left_economic =
            0.90 * communisme
          + 0.75 * regulation
          + 0.35 * ecologie
          + 0.25 * revolution

        right_economic =
            0.90 * capitalisme
          + 0.75 * laissez_faire
          + 0.35 * productivisme
          + 0.20 * reformisme

        libertarian_social =
            0.75 * constructivisme
          + 0.70 * justice_rehabilitative
          + 0.70 * progressisme
          + 0.55 * internationalisme

        authoritarian_social =
            0.75 * essentialisme
          + 0.70 * justice_punitive
          + 0.70 * conservatisme
          + 0.55 * nationalisme
        ```

        Then the model compares opposing blocks:

        ```text
        economic_raw = right_economic - left_economic
        societal_raw = authoritarian_social - libertarian_social
        ```

        A few secondary adjustments are then applied:

        ```text
        economic_raw += 0.12 * (productivisme - ecologie)
        societal_raw += 0.10 * (nationalisme - internationalisme)
        societal_raw += 0.08 * (revolution - reformisme)
        ```

        Finally, the values are normalized, compressed with a sigmoid function, and clamped to the
        plotting range:

        ```text
        economic_normalized = economic_raw / 120
        societal_normalized = societal_raw / 120

        x = 4 * sigmoid_scaled(economic_normalized)
        y = 4 * sigmoid_scaled(societal_normalized)
        ```

        The sigmoid compression prevents a single very strong opposition from sending the point too
        violently to an extreme edge of the graph.
        """
    )

    st.subheader("3. Why these weights?")

    st.markdown(
        """
        The model intentionally uses weighted sums rather than machine learning.

        Reasons:

        - the model remains explainable;
        - each input variable has a visible role;
        - the projection can be discussed and adjusted;
        - there is no labeled training dataset that would justify a statistical model.

        The highest weights are assigned to the most direct ideological indicators:

        - `communisme` and `capitalisme` strongly affect the economic axis;
        - `regulation` and `laissez_faire` strongly affect the economic axis;
        - `progressisme`, `conservatisme`, justice orientation, and social philosophy strongly affect the societal axis.

        Lower weights are used for variables that are meaningful but less directly tied to a single axis:

        - `ecologie` and `productivisme`;
        - `revolution` and `reformisme`;
        - `internationalisme` and `nationalisme`.
        """
    )

    st.subheader("4. Detailed explanation of the 16 input axes")

    axes_rows = [
        {
            "Axis": "constructivisme",
            "Meaning": "Views identities, norms, and social categories as historically and socially constructed.",
            "Effect": "Moves the profile toward the libertarian / progressive side.",
            "High score suggests": "Openness to social change, contextual analysis of norms, and less essentialist reasoning.",
        },
        {
            "Axis": "essentialisme",
            "Meaning": "Views identities, cultures, or social roles as more fixed, natural, inherited, or stable.",
            "Effect": "Moves the profile toward the authoritarian / conservative side.",
            "High score suggests": "Attachment to stable categories, inherited structures, and more traditional social interpretation.",
        },
        {
            "Axis": "justice_rehabilitative",
            "Meaning": "Prioritizes reintegration, prevention, and social causes of crime over pure punishment.",
            "Effect": "Moves the profile toward the libertarian / progressive side.",
            "High score suggests": "Support for restorative justice, rehabilitation, and reduced punitive intensity.",
        },
        {
            "Axis": "justice_punitive",
            "Meaning": "Prioritizes punishment, deterrence, order, and strict sanctions.",
            "Effect": "Moves the profile toward the authoritarian / conservative side.",
            "High score suggests": "Support for tougher penalties, stronger policing, and order-centered justice.",
        },
        {
            "Axis": "progressisme",
            "Meaning": "Supports social reforms, civil liberties, equality policies, and cultural modernization.",
            "Effect": "Moves the profile downward toward the libertarian / progressive side.",
            "High score suggests": "Preference for reforming norms and institutions toward inclusion and social change.",
        },
        {
            "Axis": "conservatisme",
            "Meaning": "Prioritizes tradition, continuity, social stability, and preservation of inherited norms.",
            "Effect": "Moves the profile upward toward the authoritarian / conservative side.",
            "High score suggests": "Preference for order, continuity, tradition, and cautious social change.",
        },
        {
            "Axis": "internationalisme",
            "Meaning": "Values cooperation beyond national borders and openness to global or supranational perspectives.",
            "Effect": "Moves the profile toward the libertarian / progressive side.",
            "High score suggests": "Support for international cooperation, cosmopolitanism, and cross-border solidarity.",
        },
        {
            "Axis": "nationalisme",
            "Meaning": "Prioritizes national sovereignty, national identity, and national interest.",
            "Effect": "Moves the profile toward the authoritarian / conservative side.",
            "High score suggests": "Preference for national priority, sovereignty, borders, and collective identity.",
        },
        {
            "Axis": "communisme",
            "Meaning": "Represents support for collective ownership, anti-capitalism, and strong redistribution.",
            "Effect": "Moves the profile strongly toward the economic left.",
            "High score suggests": "Strong opposition to capitalist ownership structures and support for collectivized economics.",
        },
        {
            "Axis": "capitalisme",
            "Meaning": "Represents support for private ownership, markets, entrepreneurship, and capital accumulation.",
            "Effect": "Moves the profile strongly toward the economic right.",
            "High score suggests": "Support for market allocation, private enterprise, and capitalist economic organization.",
        },
        {
            "Axis": "regulation",
            "Meaning": "Supports state intervention, rules, and constraints on markets.",
            "Effect": "Moves the profile toward the economic left.",
            "High score suggests": "Preference for public oversight, regulated markets, and economic correction by institutions.",
        },
        {
            "Axis": "laissez_faire",
            "Meaning": "Supports minimal state intervention and freer market dynamics.",
            "Effect": "Moves the profile toward the economic right.",
            "High score suggests": "Preference for deregulation, market autonomy, and limited economic intervention.",
        },
        {
            "Axis": "ecologie",
            "Meaning": "Prioritizes ecological sustainability, environmental constraints, and climate responsibility.",
            "Effect": "Slightly moves the profile left economically and away from productivist logic.",
            "High score suggests": "Support for environmental regulation, ecological limits, and sustainability over growth.",
        },
        {
            "Axis": "productivisme",
            "Meaning": "Prioritizes production, industrial growth, infrastructure, output, and economic expansion.",
            "Effect": "Slightly moves the profile right economically and away from ecological restraint.",
            "High score suggests": "Preference for growth, production capacity, industrial policy, and material expansion.",
        },
        {
            "Axis": "revolution",
            "Meaning": "Represents preference for rupture, radical change, and transformation of existing systems.",
            "Effect": "Slightly influences economic-left and authoritarian/libertarian posture, but is mainly a radicality signal.",
            "High score suggests": "Support for deep systemic change rather than gradual institutional reform.",
        },
        {
            "Axis": "reformisme",
            "Meaning": "Represents preference for gradual change through existing institutions.",
            "Effect": "Slightly moves away from revolutionary posture and slightly affects economic-right scoring.",
            "High score suggests": "Preference for institutional reform, gradualism, compromise, and legal continuity.",
        },
    ]

    st.dataframe(pd.DataFrame(axes_rows), use_container_width=True, hide_index=True)

    st.subheader("5. Quadrant interpretation")

    st.markdown(
        """
        | Quadrant | Interpretation |
        |---|---|
        | Left / Authoritarian | Economically left, but socially/order oriented |
        | Right / Authoritarian | Economically right, socially conservative or authority oriented |
        | Left / Libertarian | Economically left, socially progressive or libertarian |
        | Right / Libertarian | Economically right, socially liberal or libertarian |
        | Center / Moderate | Weak distance from the center or balanced contradictory tendencies |

        A central profile does not necessarily mean "no opinion". It may mean that opposite scores
        compensate each other in the 2D projection.
        """
    )

    st.subheader("6. Reference personalities and closest references")

    st.markdown(
        """
        Reference personalities are approximate anchors. They help interpret the map visually, but they
        are not ground truth.

        The closest references are computed using Euclidean distance:

        ```text
        distance = sqrt((x_profile - x_reference)^2 + (y_profile - y_reference)^2)
        ```

        A close reference means proximity in this simplified 2D space. It does not mean ideological identity.
        Two profiles can be close on the chart while differing strongly on one of the 16 raw axes.
        """
    )

    st.subheader("7. Limitations")

    st.markdown(
        """
        Main limitations:

        - the model is heuristic;
        - the 2D projection loses information;
        - the reference dataset is approximate;
        - historical figures are difficult to map onto contemporary axes;
        - no labeled calibration dataset is used;
        - nearest neighbors are interpretive, not definitive;
        - OCR can be unreliable and is intentionally excluded from the web version.

        The next planned improvement is a more detailed profile analysis that explains what each user's
        strongest and weakest scores imply about their ideological profile.
        """
    )

def main() -> None:
    _inject_css()

    personalities = _load_reference_personalities()

    _render_hero()

    filtered_personalities = _render_reference_filters(personalities)
    export_mode, closest_count = _render_sidebar_export_options()

    input_tab, graph_tab, data_tab, methodology_tab = st.tabs(
        ["Input", "Visualization", "Reference data", "Methodology"]
    )

    with input_tab:
        people = _render_multi_profile_inputs()

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