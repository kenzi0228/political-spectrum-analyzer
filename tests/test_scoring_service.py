from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.domain.models import PersonScores
from political_spectrum_analyzer.services.scoring_model_v3 import compute_scoring_model_v3_coordinates
from political_spectrum_analyzer.services.scoring_service import compute_person_result


def test_compute_person_result_returns_coordinates():
    scores = {name: 50 for name in VARIABLE_NAMES}
    person = PersonScores(name="Test", scores=scores)
    result = compute_person_result(person)

    assert isinstance(result.x, float)
    assert isinstance(result.y, float)


def test_compute_person_result_uses_scoring_model_v3_coordinates():
    scores = {name: 50 for name in VARIABLE_NAMES}
    scores.update(
        {
            "communisme": 80,
            "capitalisme": 20,
            "regulation": 75,
            "laissez_faire": 25,
            "ecologie": 70,
            "productivisme": 30,
        }
    )
    person = PersonScores(name="Model v3 profile", scores=scores)

    result = compute_person_result(person)
    expected_x, expected_y = compute_scoring_model_v3_coordinates(scores)

    assert result.x == expected_x
    assert result.y == expected_y
