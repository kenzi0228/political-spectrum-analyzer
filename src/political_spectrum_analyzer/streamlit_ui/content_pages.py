"""Static content renderers for the Streamlit interface."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st


Translate = Callable[[str, str], str]


def render_politiscales_link(language: str, translate: Translate) -> None:
    st.markdown(
        f"""
        <div class="warning-box">
            <strong>{translate(language, "politiscales_title")}</strong><br>
            {translate(language, "politiscales_description")}<br>
            <a href="https://politiscales.fr/" target="_blank" rel="noopener noreferrer">
                {translate(language, "politiscales_link_label")}
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(language: str, translate: Translate) -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">{translate(language, "hero_title")}</div>
            <div class="hero-subtitle">
                {translate(language, "hero_subtitle")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="warning-box">
            {translate(language, "hero_help")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_politiscales_link(language, translate)


def render_user_guide_tab(
    language: str,
    translate: Translate,
    markdown_text: Translate,
) -> None:
    st.header(translate(language, "guide_header"))

    st.markdown(markdown_text(language, "guide_intro"))

    step1, step2, step3 = st.columns(3)

    with step1:
        st.subheader(translate(language, "guide_step_1"))
        st.markdown(translate(language, "guide_step_1_body"))

    with step2:
        st.subheader(translate(language, "guide_step_2"))
        st.markdown(translate(language, "guide_step_2_body"))

    with step3:
        st.subheader(translate(language, "guide_step_3"))
        st.markdown(translate(language, "guide_step_3_body"))

    st.subheader(translate(language, "recommended_workflow"))
    st.markdown(markdown_text(language, "recommended_workflow_body"))

    st.subheader(translate(language, "profile_save_import"))
    st.markdown(markdown_text(language, "profile_save_import_body"))

    st.subheader(translate(language, "input_mode"))
    st.markdown(markdown_text(language, "input_mode_body"))

    st.subheader(translate(language, "reference_filters"))
    st.markdown(markdown_text(language, "reference_filters_body"))


def render_about_tab(
    language: str,
    translate: Translate,
    markdown_text: Translate,
) -> None:
    st.header(translate(language, "about_header"))

    st.markdown(translate(language, "about_intro"))

    st.subheader(translate(language, "about_for_users_title"))
    st.markdown(markdown_text(language, "about_for_users_body"))

    st.subheader(translate(language, "about_how_to_use_title"))
    st.markdown(markdown_text(language, "about_how_to_use_body"))

    st.subheader(translate(language, "about_score_title"))
    st.markdown(translate(language, "about_score_body"))

    st.subheader(translate(language, "about_privacy_title"))
    st.info(translate(language, "about_privacy_body"))

    st.subheader(translate(language, "about_desktop_title"))
    st.markdown(translate(language, "about_desktop_body"))

    render_politiscales_link(language, translate)
