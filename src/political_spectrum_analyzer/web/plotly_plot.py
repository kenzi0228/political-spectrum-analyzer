from __future__ import annotations

from typing import Iterable

import plotly.graph_objects as go

from political_spectrum_analyzer.domain.models import PersonResult, PersonalityPoint


def _confidence_scale(confidence: str | None) -> float:
    confidence = (confidence or "medium").strip().lower()

    if confidence == "high":
        return 0.85
    if confidence == "medium":
        return 1.0
    if confidence == "low":
        return 1.25

    return 1.0


def build_political_spectrum_figure(
    people: Iterable[PersonResult],
    personalities: Iterable[PersonalityPoint],
) -> go.Figure:
    """
    Build an interactive Plotly version of the political spectrum.

    The function is intentionally independent from Streamlit so it can be
    tested and reused in other web contexts.
    """
    people_list = list(people)
    personalities_list = list(personalities)

    fig = go.Figure()

    # Quadrant backgrounds
    quadrant_shapes = [
        dict(type="rect", x0=-4, x1=0, y0=0, y1=4, fillcolor="rgba(255, 204, 204, 0.35)", line_width=0, layer="below"),
        dict(type="rect", x0=0, x1=4, y0=0, y1=4, fillcolor="rgba(204, 255, 204, 0.35)", line_width=0, layer="below"),
        dict(type="rect", x0=-4, x1=0, y0=-4, y1=0, fillcolor="rgba(204, 204, 255, 0.35)", line_width=0, layer="below"),
        dict(type="rect", x0=0, x1=4, y0=-4, y1=0, fillcolor="rgba(255, 255, 204, 0.35)", line_width=0, layer="below"),
    ]

    fig.update_layout(shapes=quadrant_shapes)

    # Axis lines
    fig.add_hline(y=0, line_width=1.2, line_color="black")
    fig.add_vline(x=0, line_width=1.2, line_color="black")

    # Quadrant labels
    quadrant_labels = [
        (-2.6, 3.55, "Left / Authoritarian"),
        (2.55, 3.55, "Right / Authoritarian"),
        (-2.6, -3.55, "Left / Libertarian"),
        (2.55, -3.55, "Right / Libertarian"),
    ]

    for x, y, label in quadrant_labels:
        fig.add_annotation(
            x=x,
            y=y,
            text=label,
            showarrow=False,
            font=dict(size=12, color="rgba(0,0,0,0.45)"),
        )

    if personalities_list:
        fig.add_trace(
            go.Scatter(
                x=[person.x for person in personalities_list],
                y=[person.y for person in personalities_list],
                mode="markers+text",
                name="Reference personalities",
                text=[person.name for person in personalities_list],
                textposition="top center",
                marker=dict(
                    size=[
                        16 * _confidence_scale(getattr(person, "confidence", "medium"))
                        for person in personalities_list
                    ],
                    color="rgba(90,90,90,0.45)",
                    line=dict(width=1, color="black"),
                ),
                customdata=[
                    [
                        person.display_group,
                        person.country or "",
                        person.period or "",
                        person.ideology_family or "",
                        person.confidence,
                    ]
                    for person in personalities_list
                ],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Group: %{customdata[0]}<br>"
                    "Country: %{customdata[1]}<br>"
                    "Period: %{customdata[2]}<br>"
                    "Ideology: %{customdata[3]}<br>"
                    "Confidence: %{customdata[4]}<br>"
                    "x=%{x:.2f}, y=%{y:.2f}"
                    "<extra></extra>"
                ),
            )
        )

    if people_list:
        fig.add_trace(
            go.Scatter(
                x=[person.x for person in people_list],
                y=[person.y for person in people_list],
                mode="markers+text",
                name="User profiles",
                text=[person.name for person in people_list],
                textposition="top right",
                marker=dict(
                    size=18,
                    symbol="x",
                    color="#1f77b4",
                    line=dict(width=2, color="black"),
                ),
                customdata=[
                    [person.name, round(person.x, 3), round(person.y, 3)]
                    for person in people_list
                ],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "x=%{customdata[1]}, y=%{customdata[2]}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title="Political Spectrum Projection",
        xaxis_title="Economic axis: Left < 0 | Right > 0",
        yaxis_title="Societal axis: Libertarian < 0 | Authoritarian > 0",
        xaxis=dict(range=[-4, 4], zeroline=False),
        yaxis=dict(range=[-4, 4], zeroline=False),
        height=650,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=40, r=40, t=80, b=40),
    )

    return fig