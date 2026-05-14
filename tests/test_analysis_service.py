from political_spectrum_analyzer.domain.models import PersonResult, PersonalityPoint
from political_spectrum_analyzer.services.analysis_service import (
    analyze_profile,
    compute_distance,
    get_quadrant,
)


def test_compute_distance_returns_euclidean_distance():
    assert compute_distance(0, 0, 3, 4) == 5


def test_get_quadrant_detects_left_authoritarian():
    assert get_quadrant(-2.0, 1.5) == "Left / Authoritarian"


def test_get_quadrant_detects_center_moderate():
    assert get_quadrant(0.1, -0.1) == "Center / Moderate"


def test_analyze_profile_returns_closest_references():
    person = PersonResult(
        name="Test profile",
        scores={},
        x=-1.0,
        y=0.5,
    )

    personalities = [
        PersonalityPoint(
            name="Far reference",
            display_group="Test",
            x=3.0,
            y=3.0,
        ),
        PersonalityPoint(
            name="Close reference",
            display_group="Test",
            x=-1.1,
            y=0.6,
        ),
    ]

    analysis = analyze_profile(person, personalities, top_n=1)

    assert analysis.name == "Test profile"
    assert analysis.quadrant == "Left / Authoritarian"
    assert analysis.closest_references[0].name == "Close reference"
