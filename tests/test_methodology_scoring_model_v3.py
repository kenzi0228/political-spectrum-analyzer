from pathlib import Path

import pytest

from political_spectrum_analyzer.services.scoring_model_v3 import (
    compute_scoring_model_v3_blocks,
    compute_scoring_model_v3_coordinates,
    scale_axis_v3,
)


APP = Path("streamlit_app.py")
METHODOLOGY = Path("src/political_spectrum_analyzer/streamlit_ui/methodology.py")


def _methodology_v3_body() -> str:
    return METHODOLOGY.read_text(encoding="utf-8")


def test_methodology_uses_v3_coefficients_and_tanh():
    body = _methodology_v3_body()

    assert "0.95 * communisme" in body
    assert "0.80 * laissez_faire" in body
    assert "0.28 * ecologie" in body
    assert "0.24 * productivisme" in body
    assert "0.35 * internationalisme" in body
    assert "0.60 * essentialisme" in body
    assert "0.70 * justice_punitive" in body
    assert "0.70 * conservatisme" in body
    assert "0.30 * nationalisme" in body
    assert "0.04 * (productivisme - ecologie)" in body
    assert "0.03 * (nationalisme - internationalisme)" in body
    assert "tanh(0.015" in body


def test_methodology_removes_old_coordinate_formula():
    body = _methodology_v3_body()

    assert "0.25 * revolution" not in body
    assert "0.20 * reformisme" not in body
    assert "0.08 * (revolution - reformisme)" not in body
    assert "raw / 120" not in body
    assert "sigmoid_scaled" not in body


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


def test_scoring_model_v3_excludes_revolution_reformism_from_coordinate_blocks():
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

    blocks_with_revolution = compute_scoring_model_v3_blocks(scores)

    scores["revolution"] = 0
    scores["reformisme"] = 100
    blocks_with_reformism = compute_scoring_model_v3_blocks(scores)

    assert blocks_with_revolution["economic_raw"] == blocks_with_reformism["economic_raw"]
    assert blocks_with_revolution["social_raw"] == blocks_with_reformism["social_raw"]


def test_scoring_model_v3_uses_reduced_ecology_productivism_and_sovereignty_weights():
    blocks = compute_scoring_model_v3_blocks({
        "ecologie": 100,
        "productivisme": 100,
        "internationalisme": 100,
        "nationalisme": 100,
    })

    assert blocks["economic_left"] == pytest.approx(28.0)
    assert blocks["economic_right"] == pytest.approx(24.0)
    assert blocks["social_libertarian"] == pytest.approx(35.0)
    assert blocks["social_authoritarian"] == pytest.approx(30.0)


def test_scoring_model_v3_coordinates_are_bounded():
    x, y = compute_scoring_model_v3_coordinates({
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
    assert scale_axis_v3(0) == 0
