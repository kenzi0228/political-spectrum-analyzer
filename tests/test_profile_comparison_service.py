from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.services.profile_comparison_service import (
    build_comparison_rows,
    build_profile_comparisons,
    compare_profiles,
    compute_coordinate_distance,
    compute_similarity_score,
)


def _person(name: str, x: float, y: float, scores: dict[str, float]) -> PersonResult:
    return PersonResult(name=name, x=x, y=y, scores=scores)


def test_coordinate_distance_uses_euclidean_distance():
    first = _person("A", 0.0, 0.0, {})
    second = _person("B", 3.0, 4.0, {})

    assert compute_coordinate_distance(first, second) == 5.0


def test_similarity_score_is_high_for_close_profiles():
    assert compute_similarity_score(0.0) == 100.0
    assert compute_similarity_score(8.0) == 0.0
    assert compute_similarity_score(4.0) == 50.0


def test_compare_profiles_detects_shared_axes_and_gaps():
    first = _person(
        "A",
        -1.0,
        0.5,
        {
            "progressisme": 80,
            "ecologie": 75,
            "capitalisme": 20,
            "nationalisme": 10,
        },
    )
    second = _person(
        "B",
        -1.5,
        0.2,
        {
            "progressisme": 85,
            "ecologie": 70,
            "capitalisme": 65,
            "nationalisme": 15,
        },
    )

    comparison = compare_profiles(first, second)

    assert comparison.first_name == "A"
    assert comparison.second_name == "B"
    assert comparison.ideological_similarity_score > 80
    assert "progressisme" in comparison.shared_strong_axes
    assert "ecologie" in comparison.shared_strong_axes
    assert comparison.largest_score_gaps[0].axis == "capitalisme"
    assert "A and B" in comparison.summary


def test_build_profile_comparisons_returns_all_pairs():
    people = [
        _person("A", 0.0, 0.0, {}),
        _person("B", 1.0, 1.0, {}),
        _person("C", 2.0, 2.0, {}),
    ]

    comparisons = build_profile_comparisons(people)

    assert len(comparisons) == 3


def test_build_comparison_rows_is_table_friendly():
    people = [
        _person("A", 0.0, 0.0, {"progressisme": 80}),
        _person("B", 1.0, 1.0, {"progressisme": 75}),
    ]

    rows = build_comparison_rows(build_profile_comparisons(people))

    assert len(rows) == 1
    assert rows[0]["first_profile"] == "A"
    assert rows[0]["second_profile"] == "B"
    assert "ideological_similarity_score" in rows[0]
    assert "summary" in rows[0]