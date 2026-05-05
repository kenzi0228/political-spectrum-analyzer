from political_spectrum_analyzer.config import PERSONALITIES_CSV_PATH
from political_spectrum_analyzer.services.personalities_service import load_personalities


def test_load_personalities_returns_data():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)
    assert len(personalities) > 0