import math

from political_spectrum_analyzer.model.scoring_model_v2 import (
    ECONOMIC_LEFT_WEIGHTS,
    ECONOMIC_RIGHT_WEIGHTS,
    NORMALIZATION_DENOMINATOR,
    SOCIAL_AUTHORITARIAN_WEIGHTS,
    SOCIAL_LIBERTARIAN_WEIGHTS,
    compute_position,
    compute_projection_breakdown,
    compute_secondary_dimensions,
    scale_raw_score,
    sigmoid_scaled,
)


def test_v2_primary_weights_match_documented_model():
    assert ECONOMIC_LEFT_WEIGHTS == {
        "communisme": 0.90,
        "regulation": 0.70,
        "ecologie": 0.35,
        "revolution": 0.25,
    }
    assert ECONOMIC_RIGHT_WEIGHTS == {
        "capitalisme": 0.90,
        "laissez_faire": 0.75,
        "productivisme": 0.25,
        "reformisme": 0.20,
    }
    assert SOCIAL_LIBERTARIAN_WEIGHTS["internationalisme"] == 0.50
    assert SOCIAL_AUTHORITARIAN_WEIGHTS["nationalisme"] == 0.50


def test_sigmoid_scaling_is_bounded_and_symmetric():
    assert scale_raw_score(0) == 0
    assert scale_raw_score(10) > 0
    assert scale_raw_score(-10) < 0
    assert abs(scale_raw_score(1000)) <= 4
    assert sigmoid_scaled(0) == 0
    assert math.isclose(scale_raw_score(80), 4 * sigmoid_scaled(80 / NORMALIZATION_DENOMINATOR))


def test_left_ecological_profile_moves_left():
    scores = {
        "communisme": 60,
        "regulation": 70,
        "ecologie": 90,
        "capitalisme": 10,
        "laissez_faire": 10,
        "productivisme": 20,
    }

    x, _ = compute_position(scores)

    assert x < -2.0


def test_market_productivist_profile_moves_right():
    scores = {
        "communisme": 5,
        "regulation": 10,
        "ecologie": 10,
        "capitalisme": 90,
        "laissez_faire": 85,
        "productivisme": 80,
    }

    x, _ = compute_position(scores)

    assert x > 2.0


def test_secondary_dimensions_keep_change_method():
    scores = {
        "revolution": 85,
        "reformisme": 20,
        "productivisme": 30,
        "ecologie": 80,
        "internationalisme": 70,
        "nationalisme": 25,
        "justice_rehabilitative": 60,
        "justice_punitive": 30,
        "progressisme": 75,
        "conservatisme": 20,
    }

    dimensions = compute_secondary_dimensions(scores)

    assert dimensions["change_method"] == 65
    assert dimensions["eco_productivism_balance"] == -50
    assert dimensions["globalism_balance"] == 45
    assert dimensions["justice_balance"] == 30
    assert dimensions["social_change_balance"] == 55


def test_projection_breakdown_exposes_raw_blocks_and_coordinates():
    scores = {
        "communisme": 50,
        "regulation": 50,
        "ecologie": 50,
        "capitalisme": 50,
        "laissez_faire": 50,
        "productivisme": 50,
        "constructivisme": 50,
        "justice_rehabilitative": 50,
        "progressisme": 50,
        "internationalisme": 50,
        "essentialisme": 50,
        "justice_punitive": 50,
        "conservatisme": 50,
        "nationalisme": 50,
        "revolution": 50,
        "reformisme": 50,
    }

    breakdown = compute_projection_breakdown(scores)

    assert hasattr(breakdown, "economic_left")
    assert hasattr(breakdown, "economic_right")
    assert hasattr(breakdown, "strategic_adjustment")
    assert hasattr(breakdown, "economic_normalized")
    assert hasattr(breakdown, "x_raw")
    assert hasattr(breakdown, "secondary_dimensions")
    assert -4 <= breakdown.x <= 4
    assert -4 <= breakdown.y <= 4
