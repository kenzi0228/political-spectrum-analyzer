from political_spectrum_analyzer.services.profile_interpretation_service import (
    build_profile_archetype,
    build_tension_reading,
    get_axis_pair_balances,
    get_dominant_axes,
    get_weak_axes,
    interpret_profile,
)


def test_dominant_axes_are_sorted_descending():
    scores = {
        "capitalisme": 90,
        "laissez_faire": 80,
        "progressisme": 20,
    }

    result = get_dominant_axes(scores, limit=2)

    assert result[0].axis == "capitalisme"
    assert result[1].axis == "laissez_faire"


def test_weak_axes_are_sorted_ascending():
    scores = {
        "capitalisme": 90,
        "laissez_faire": 80,
        "progressisme": 20,
    }

    result = get_weak_axes(scores, limit=1)

    assert result[0].axis == "constructivisme"


def test_axis_pair_balances_include_all_pairs():
    scores = {
        "communisme": 70,
        "capitalisme": 20,
        "regulation": 80,
        "laissez_faire": 10,
    }

    balances = get_axis_pair_balances(scores)

    assert len(balances) == 8
    assert any(row["dimension"] == "Ownership model" for row in balances)


def test_interpret_profile_returns_readable_sections():
    scores = {
        "communisme": 80,
        "regulation": 75,
        "progressisme": 70,
        "reformisme": 65,
    }

    interpretation = interpret_profile("Test", scores)

    assert interpretation.profile_name == "Test"
    assert interpretation.dominant_axes
    assert interpretation.weak_axes
    assert interpretation.axis_pair_balances
    assert "Test" in interpretation.synthesis
    assert interpretation.economic_reading
    assert interpretation.societal_reading
    assert interpretation.strategic_reading
    assert interpretation.archetype
    assert interpretation.tension_reading
    assert interpretation.profile_highlights


def test_archetype_changes_with_scores():
    left_progressive = build_profile_archetype(
        {
            "communisme": 90,
            "regulation": 90,
            "progressisme": 90,
            "constructivisme": 90,
            "justice_rehabilitative": 90,
            "internationalisme": 90,
        }
    )

    right_conservative = build_profile_archetype(
        {
            "capitalisme": 90,
            "laissez_faire": 90,
            "productivisme": 90,
            "conservatisme": 90,
            "essentialisme": 90,
            "justice_punitive": 90,
            "nationalisme": 90,
        }
    )

    assert left_progressive != right_conservative


def test_tension_reading_is_not_empty():
    reading = build_tension_reading(
        {
            "communisme": 90,
            "capitalisme": 10,
        }
    )

    assert reading