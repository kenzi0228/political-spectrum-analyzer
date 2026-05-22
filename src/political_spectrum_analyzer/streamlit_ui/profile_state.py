"""Profile state helpers for the Streamlit app."""

from __future__ import annotations

import streamlit as st

from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.model.scoring_model_v2 import compute_position


PROFILE_SNAPSHOT_KEY = "profile_state_snapshot"


def profile_state_prefix(profile_index: int) -> str:
    return f"profile_{profile_index}"


def _profile_snapshots() -> list[dict[str, object]]:
    snapshots = st.session_state.get(PROFILE_SNAPSHOT_KEY, [])
    return snapshots if isinstance(snapshots, list) else []


def profile_count_from_state() -> int:
    try:
        fallback_count = len(_profile_snapshots()) or 1
        return max(1, min(8, int(st.session_state.get("profile_count", fallback_count))))
    except Exception:
        return 1


def build_person_result(profile_name: str, scores: dict[str, int]) -> PersonResult:
    x, y = compute_position(scores)

    return PersonResult(
        name=profile_name.strip() or "Profile",
        scores=scores,
        x=float(x),
        y=float(y),
    )


def persist_people_to_state(people: list[PersonResult]) -> None:
    """Keep profile data available when Streamlit temporarily unmounts input widgets."""
    st.session_state[PROFILE_SNAPSHOT_KEY] = [
        {
            "name": person.name,
            "scores": {
                axis: int(person.scores.get(axis, 0))
                for axis in VARIABLE_NAMES
            },
        }
        for person in people
    ]


def build_people_from_state() -> list[PersonResult]:
    people: list[PersonResult] = []
    snapshots = _profile_snapshots()

    for profile_index in range(profile_count_from_state()):
        prefix = profile_state_prefix(profile_index)
        snapshot = snapshots[profile_index] if profile_index < len(snapshots) and isinstance(snapshots[profile_index], dict) else {}
        snapshot_scores = snapshot.get("scores", {}) if isinstance(snapshot.get("scores", {}), dict) else {}
        profile_name = str(
            st.session_state.get(
                f"{prefix}_name",
                snapshot.get("name", f"Profile {profile_index + 1}"),
            )
        )
        scores = {
            axis: int(st.session_state.get(f"{prefix}_{axis}", snapshot_scores.get(axis, 0)))
            for axis in VARIABLE_NAMES
        }
        people.append(build_person_result(profile_name, scores))

    return people
