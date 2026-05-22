"""Profile state helpers for the Streamlit app."""

from __future__ import annotations

import streamlit as st

from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.services.scoring_model_v3 import compute_scoring_model_v3_coordinates


def profile_state_prefix(profile_index: int) -> str:
    return f"profile_{profile_index}"


def profile_count_from_state() -> int:
    try:
        return max(1, min(8, int(st.session_state.get("profile_count", 1))))
    except Exception:
        return 1


def build_person_result(profile_name: str, scores: dict[str, int]) -> PersonResult:
    x, y = compute_scoring_model_v3_coordinates(scores)

    return PersonResult(
        name=profile_name.strip() or "Profile",
        scores=scores,
        x=float(x),
        y=float(y),
    )


def build_people_from_state() -> list[PersonResult]:
    people: list[PersonResult] = []

    for profile_index in range(profile_count_from_state()):
        prefix = profile_state_prefix(profile_index)
        profile_name = str(st.session_state.get(f"{prefix}_name", f"Profile {profile_index + 1}"))
        scores = {
            axis: int(st.session_state.get(f"{prefix}_{axis}", 0))
            for axis in VARIABLE_NAMES
        }
        people.append(build_person_result(profile_name, scores))

    return people
