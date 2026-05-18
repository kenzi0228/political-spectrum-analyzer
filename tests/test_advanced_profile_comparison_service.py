from political_spectrum_analyzer.domain.models import PersonResult
from political_spectrum_analyzer.services.advanced_profile_comparison_service import (
    build_advanced_comparison_rows,
    build_advanced_profile_comparisons,
    build_similarity_matrix,
    compare_profiles_advanced,
    compute_economic_similarity,
    compute_global_similarity,
    compute_secondary_similarity,
    compute_societal_similarity,
)


def _person(name: str, x: float, y: float, scores: dict[str, float]) -> PersonResult:
    return PersonResult(name=name, x=x, y=y, scores=scores)


def test_global_similarity_is_high_for_close_coordinates():
    first = _person("A", 0.0, 0.0, {})
    second = _person("B", 0.5, 0.5, {})

    assert compute_global_similarity(first, second) > 90


def test_domain_specific_similarity_scores_are_available():
    first = _person(
        "A",
        -1.0,
        0.0,
        {
            "communisme": 80,
            "capitalisme": 10,
            "progressisme": 80,
            "conservatisme": 10,
            "revolution": 70,
            "reformisme": 20,
        },
    )
    second = _person(
        "B",
        -1.2,
        0.1,
        {
            "communisme": 75,
            "capitalisme": 15,
            "progressisme": 70,
            "conservatisme": 20,
            "revolution": 65,
            "reformisme": 25,
        },
    )

    assert compute_economic_similarity(first, second) > 80
    assert compute_societal_similarity(first, second) > 80
    assert compute_secondary_similarity(first, second) > 80


def test_compare_profiles_advanced_exposes_secondary_gaps():
    first = _person(
        "A",
        -1.0,
        0.0,
        {
            "revolution": 90,
            "reformisme": 10,
            "internationalisme": 80,
            "nationalisme": 15,
            "communisme": 80,
            "capitalisme": 10,
        },
    )
    second = _person(
        "B",
        1.0,
        0.0,
        {
            "revolution": 10,
            "reformisme": 90,
            "internationalisme": 20,
            "nationalisme": 75,
            "communisme": 10,
            "capitalisme": 80,
        },
    )

    comparison = compare_profiles_advanced(first, second)

    assert comparison.global_similarity_score < 100
    assert comparison.economic_similarity_score < 100
    assert comparison.secondary_dimension_gaps
    assert comparison.most_divergent_dimension
    assert "A and B" in comparison.summary


def test_build_advanced_profile_comparisons_returns_all_pairs():
    people = [
        _person("A", 0.0, 0.0, {}),
        _person("B", 1.0, 1.0, {}),
        _person("C", 2.0, 2.0, {}),
    ]

    comparisons = build_advanced_profile_comparisons(people)

    assert len(comparisons) == 3


def test_advanced_comparison_rows_and_matrix_are_table_friendly():
    people = [
        _person("A", 0.0, 0.0, {"communisme": 80}),
        _person("B", 1.0, 1.0, {"communisme": 70}),
    ]

    comparisons = build_advanced_profile_comparisons(people)
    rows = build_advanced_comparison_rows(comparisons)
    matrix = build_similarity_matrix(people)

    assert rows
    assert "economic_similarity_score" in rows[0]
    assert "secondary_similarity_score" in rows[0]
    assert matrix[0]["profile"] == "A"
    assert "B" in matrix[0]
