"""Navigation helpers for the Streamlit app."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st


Translate = Callable[[str, str], str]


def active_view_options(language: str, translate: Translate) -> dict[str, str]:
    return {
        "input": translate(language, "tab_input"),
        "guide": translate(language, "tab_guide"),
        "visualization": translate(language, "tab_visualization"),
        "reference": translate(language, "tab_reference"),
        "methodology": translate(language, "tab_methodology"),
    }


def render_active_view_selector(language: str, translate: Translate) -> str:
    options = active_view_options(language, translate)
    return st.sidebar.radio(
        translate(language, "active_tab_label"),
        options=list(options.keys()),
        index=0,
        format_func=lambda value: options.get(value, value),
        help=translate(language, "active_tab_help"),
        key="active_tab_label",
    )


def view_requires_reference_dataset(active_view: str) -> bool:
    return active_view in {"visualization", "reference"}


def render_inactive_view_notice(view_label: str, language: str, translate: Translate) -> None:
    st.info(translate(language, "inactive_tab_notice").format(view_label=view_label))
