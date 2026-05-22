from pathlib import Path

import pytest

from political_spectrum_analyzer.model.scoring_model_v2 import (
    compute_position,
    compute_projection_breakdown,
    scale_raw_score,
)


APP = Path("streamlit_app.py")
METHODOLOGY = Path("src/political_spectrum_analyzer/streamlit_ui/methodology.py")


def _methodology_v3_body() -> str:
    return METHODOLOGY.read_text(encoding="utf-8")


def test_methodology_documents_current_v2_coefficients_and_sigmoid():
    body = _methodology_v3_body()

    assert "scoring model v2" in body
    assert "0.90 * communisme" in body
    assert "0.75 * laissez_faire" in body
    assert "0.35 * ecologie" in body
    assert "0.25 * productivisme" in body
    assert "0.50 * internationalisme" in body
    assert "0.60 * essentialisme" in body
    assert "0.70 * justice_punitive" in body
    assert "0.70 * conservatisme" in body
    assert "0.50 * nationalisme" in body
    assert "0.12 * (productivisme - ecologie)" in body
    assert "0.10 * (nationalisme - internationalisme)" in body
    assert "0.08 * (revolution - reformisme)" in body
    assert "sigmoid_scaled" in body


def test_methodology_includes_v2_coordinate_formula():
    body = _methodology_v3_body()

    assert "0.25 * revolution" in body
    assert "0.20 * reformisme" in body
    assert "economic_normalized = economic_raw / 120" in body
    assert "social_normalized = social_raw / 120" in body


def test_methodology_does_not_contain_about_guide_footer():
    body = _methodology_v3_body()

    assert "About this analyzer" not in body
    assert "Need to take or retake the test" not in body
    assert "Open Politiscales test" not in body


def test_main_calls_methodology_v3_in_methodology_tab():
    content = APP.read_text(encoding="utf-8")
    main_start = content.index("def main")
    entrypoint = content.rfind('if __name__ == "__main__"')
    main_body = content[main_start:entrypoint]

    assert "with methodology_tab:" in main_body
    assert "_render_methodology_v3(language)" in main_body
    assert "render_methodology_v3 as _render_methodology_v3" in content


def test_current_v2_uses_revolution_reformism_in_coordinate_blocks():
    scores = {
        "communisme": 40,
        "capitalisme": 10,
        "regulation": 35,
        "laissez_faire": 5,
        "ecologie": 30,
        "productivisme": 8,
        "constructivisme": 20,
        "essentialisme": 5,
        "justice_rehabilitative": 25,
        "justice_punitive": 4,
        "progressisme": 30,
        "conservatisme": 3,
        "internationalisme": 20,
        "nationalisme": 4,
        "revolution": 100,
        "reformisme": 0,
    }

    blocks_with_revolution = compute_projection_breakdown(scores)

    scores["revolution"] = 0
    scores["reformisme"] = 100
    blocks_with_reformism = compute_projection_breakdown(scores)

    assert blocks_with_revolution.x_raw != blocks_with_reformism.x_raw
    assert blocks_with_revolution.y_raw != blocks_with_reformism.y_raw


def test_current_v2_uses_documented_ecology_productivism_and_sovereignty_weights():
    blocks = compute_projection_breakdown({
        "ecologie": 100,
        "productivisme": 100,
        "internationalisme": 100,
        "nationalisme": 100,
    })

    assert blocks.economic_left == pytest.approx(35.0)
    assert blocks.economic_right == pytest.approx(25.0)
    assert blocks.social_libertarian == pytest.approx(50.0)
    assert blocks.social_authoritarian == pytest.approx(50.0)


def test_current_v2_coordinates_are_bounded():
    x, y = compute_position({
        "capitalisme": 100,
        "laissez_faire": 100,
        "productivisme": 100,
        "essentialisme": 100,
        "justice_punitive": 100,
        "conservatisme": 100,
        "nationalisme": 100,
    })

    assert -4 <= x <= 4
    assert -4 <= y <= 4
    assert scale_raw_score(0) == 0
