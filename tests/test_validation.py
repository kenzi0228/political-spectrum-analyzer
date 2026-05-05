from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.domain.validation import validate_scores


def test_validate_scores_accepts_valid_payload():
    scores = {name: 50 for name in VARIABLE_NAMES}
    validate_scores(scores)