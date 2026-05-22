"""Runtime CSS helpers for the Streamlit app."""

from __future__ import annotations

import streamlit as st


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


FORCE_DARK_SIDEBAR_CSS = """
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111522 0%, #0E1117 100%) !important;
}
[data-testid="stSidebar"] * {
    color: #FAFAFA !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="base-input"] {
    background-color: #1A1D2E !important;
    color: #FAFAFA !important;
    border-color: rgba(255,255,255,0.18) !important;
}
</style>
"""


PROFILE_METRIC_DARK_CSS = """
<style>
[data-testid="metric-container"],
[data-testid="stMetric"],
div[data-testid="stMetric"] {
    background: #111522 !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
    color: #FAFAFA !important;
}
[data-testid="metric-container"] *,
[data-testid="stMetric"] *,
div[data-testid="stMetric"] * {
    color: #FAFAFA !important;
}
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: #FAFAFA !important;
}
div[data-testid="column"] div[style*="background-color: rgb(255, 255, 255)"],
div[data-testid="column"] div[style*="background: rgb(255, 255, 255)"] {
    background: #111522 !important;
    color: #FAFAFA !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
}
div[data-testid="column"] div[style*="background-color: rgb(255, 255, 255)"] *,
div[data-testid="column"] div[style*="background: rgb(255, 255, 255)"] * {
    color: #FAFAFA !important;
}
</style>
"""


def inject_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def force_dark_sidebar() -> None:
    st.markdown(FORCE_DARK_SIDEBAR_CSS, unsafe_allow_html=True)


def force_dark_metric_cards() -> None:
    st.markdown(PROFILE_METRIC_DARK_CSS, unsafe_allow_html=True)
