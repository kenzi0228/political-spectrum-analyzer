from political_spectrum_analyzer.services.advanced_profile_interpretation_service import (
    build_advanced_interpretation_rows,
    build_advanced_profile_interpretation,
    compute_coherence_score,
    compute_intensity_score,
    compute_radicality_score,
)


def test_intensity_score_increases_with_extreme_values():
    assert compute_intensity_score({"communisme": 95, "capitalisme": 5}) > compute_intensity_score({"communisme": 50, "capitalisme": 50})


def test_coherence_score_penalizes_opposing_high_scores():
    assert compute_coherence_score({"communisme": 90, "capitalisme": 10}) > compute_coherence_score({"communisme": 90, "capitalisme": 90})


def test_radicality_score_uses_revolution_minus_reformism():
    assert compute_radicality_score({"revolution": 85, "reformisme": 20}) == 65


def test_advanced_interpretation_contains_secondary_dimensions():
    scores = {
        "communisme": 70,
        "regulation": 80,
        "ecologie": 90,
        "capitalisme": 10,
        "laissez_faire": 15,
        "productivisme": 20,
        "constructivisme": 75,
        "justice_rehabilitative": 70,
        "progressisme": 85,
        "internationalisme": 80,
        "essentialisme": 20,
        "justice_punitive": 15,
        "conservatisme": 25,
        "nationalisme": 10,
        "revolution": 60,
        "reformisme": 30,
    }
    interpretation = build_advanced_profile_interpretation("Test", scores)
    assert interpretation.profile_name == "Test"
    assert "change_method" in interpretation.secondary_dimensions
    assert interpretation.dominant_axes
    assert interpretation.weak_axes
    assert "profile" in interpretation.short_summary.lower()


def test_advanced_interpretation_rows_are_table_friendly():
    interpretation = build_advanced_profile_interpretation("A", {"communisme": 70, "capitalisme": 20, "revolution": 80, "reformisme": 25})
    rows = build_advanced_interpretation_rows([interpretation])
    assert rows[0]["profile_name"] == "A"
    assert "coherence_score" in rows[0]
    assert "change_method" in rows[0]
