from political_spectrum_analyzer.domain.models import PersonalityPoint
from political_spectrum_analyzer.services.personality_filter_service import (
    ANY_VALUE,
    filter_personalities,
    get_unique_values,
)


def _sample_personalities():
    return [
        PersonalityPoint(
            name="Karl Marx",
            display_group="Philosopher",
            country="Germany",
            period="19th century",
            ideology_family="Socialism",
            x=-2.8,
            y=-0.8,
        ),
        PersonalityPoint(
            name="Emmanuel Macron",
            display_group="President",
            country="France",
            period="21st century",
            ideology_family="Centrism",
            x=1.0,
            y=0.2,
        ),
        PersonalityPoint(
            name="Charles de Gaulle",
            display_group="President",
            country="France",
            period="20th century",
            ideology_family="Gaullism",
            x=1.8,
            y=1.3,
        ),
    ]


def test_get_unique_values_includes_any_value():
    values = get_unique_values(_sample_personalities(), "display_group")

    assert values[0] == ANY_VALUE
    assert "Philosopher" in values
    assert "President" in values


def test_filter_personalities_by_display_group():
    result = filter_personalities(
        _sample_personalities(),
        display_group="President",
    )

    assert len(result) == 2
    assert all(person.display_group == "President" for person in result)


def test_filter_personalities_by_country_and_period():
    result = filter_personalities(
        _sample_personalities(),
        country="France",
        period="20th century",
    )

    assert len(result) == 1
    assert result[0].name == "Charles de Gaulle"


def test_filter_personalities_with_any_values_returns_all():
    result = filter_personalities(
        _sample_personalities(),
        display_group=ANY_VALUE,
        country=ANY_VALUE,
        period=ANY_VALUE,
        ideology_family=ANY_VALUE,
    )

    assert len(result) == 3