from political_spectrum_analyzer.config import PERSONALITIES_CSV_PATH
from political_spectrum_analyzer.services.personalities_service import load_personalities


def test_load_personalities_returns_data():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)
    assert len(personalities) > 0


def test_load_personalities_includes_metadata_fields():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)
    marx = next(person for person in personalities if person.name == "Karl Marx")

    assert marx.country == "Germany"
    assert marx.period == "19th century"
    assert marx.ideology_family == "Socialism"
    assert marx.confidence == "medium"


def test_load_personalities_keeps_coordinates_as_float():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)
    marx = next(person for person in personalities if person.name == "Karl Marx")

    assert isinstance(marx.x, float)
    assert isinstance(marx.y, float)
    assert isinstance(marx.ux, float)
    assert isinstance(marx.uy, float)