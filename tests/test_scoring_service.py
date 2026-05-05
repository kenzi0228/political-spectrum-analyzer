from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.domain.models import PersonScores
from political_spectrum_analyzer.services.scoring_service import compute_person_result


def test_compute_person_result_returns_coordinates():
    scores = {name: 50 for name in VARIABLE_NAMES}
    person = PersonScores(name="Test", scores=scores)
    result = compute_person_result(person)

    assert isinstance(result.x, float)
    assert isinstance(result.y, float)