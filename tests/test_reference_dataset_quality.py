from political_spectrum_analyzer.config import PERSONALITIES_CSV_PATH
from political_spectrum_analyzer.services.personalities_service import load_personalities


VALID_CONFIDENCE_LEVELS = {"high", "medium", "low"}


def _country_tokens(country: str | None) -> set[str]:
    if not country:
        return set()

    return {part.strip().lower() for part in country.split(";") if part.strip()}


def test_reference_dataset_has_exactly_150_entries():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)
    assert len(personalities) == 250


def test_reference_dataset_names_are_unique():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)
    names = [person.name for person in personalities]

    assert len(names) == len(set(names))


def test_reference_dataset_coordinates_are_within_plot_bounds():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)

    for person in personalities:
        assert -4.0 <= person.x <= 4.0
        assert -4.0 <= person.y <= 4.0


def test_reference_dataset_uncertainty_values_are_positive():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)

    for person in personalities:
        assert person.ux > 0
        assert person.uy > 0


def test_reference_dataset_confidence_values_are_valid():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)

    for person in personalities:
        assert person.confidence in VALID_CONFIDENCE_LEVELS


def test_reference_dataset_core_metadata_is_present():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)

    for person in personalities:
        assert person.display_group
        assert person.country
        assert person.period
        assert person.ideology_family


def test_reference_dataset_contains_no_israel_country_entries():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)

    for person in personalities:
        assert "israel" not in _country_tokens(person.country)


def test_reference_dataset_country_separator_supports_multi_country_entries():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)

    multi_country_entries = [
        person for person in personalities if person.country and ";" in person.country
    ]

    assert len(multi_country_entries) > 0


def test_reference_dataset_has_reasonable_country_diversity():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)

    countries = set()
    for person in personalities:
        countries.update(_country_tokens(person.country))

    assert len(countries) >= 30


def test_reference_dataset_has_simplified_ideology_categories():
    personalities = load_personalities(PERSONALITIES_CSV_PATH)
    ideologies = {person.ideology_family for person in personalities if person.ideology_family}

    assert 8 <= len(ideologies) <= 35