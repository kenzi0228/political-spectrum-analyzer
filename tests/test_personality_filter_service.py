from political_spectrum_analyzer.domain.models import PersonalityPoint
from political_spectrum_analyzer.services.personality_filter_service import (
    ANY_VALUE,
    NONE_VALUE,
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
            name="Albert Camus",
            display_group="Philosopher",
            country="France; Algeria",
            period="20th century",
            ideology_family="Liberalism",
            x=-0.4,
            y=-0.8,
        ),
        PersonalityPoint(
            name="Charles de Gaulle",
            display_group="President",
            country="France",
            period="20th century",
            ideology_family="Conservatism",
            x=1.8,
            y=1.3,
        ),
    ]


def test_get_unique_values_includes_none_and_any_values():
    values = get_unique_values(_sample_personalities(), "display_group")

    assert values[0] == NONE_VALUE
    assert values[1] == ANY_VALUE
    assert "Philosopher" in values
    assert "President" in values


def test_get_unique_values_splits_multi_country_values():
    values = get_unique_values(_sample_personalities(), "country")

    assert values[0] == NONE_VALUE
    assert values[1] == ANY_VALUE
    assert "France" in values
    assert "Algeria" in values


def test_filter_personalities_all_none_returns_no_references():
    result = filter_personalities(
        _sample_personalities(),
        display_group=NONE_VALUE,
        country=NONE_VALUE,
        period=NONE_VALUE,
        ideology_family=NONE_VALUE,
    )

    assert result == []


def test_filter_personalities_defaults_return_no_references():
    result = filter_personalities(_sample_personalities())

    assert result == []


def test_filter_personalities_all_any_returns_all_references():
    result = filter_personalities(
        _sample_personalities(),
        display_group=ANY_VALUE,
        country=ANY_VALUE,
        period=ANY_VALUE,
        ideology_family=ANY_VALUE,
    )

    assert len(result) == 3


def test_filter_personalities_by_display_group_with_other_filters_none():
    result = filter_personalities(
        _sample_personalities(),
        display_group="President",
        country=NONE_VALUE,
        period=NONE_VALUE,
        ideology_family=NONE_VALUE,
    )

    assert len(result) == 1
    assert result[0].name == "Charles de Gaulle"


def test_filter_personalities_by_multi_country_token():
    result = filter_personalities(
        _sample_personalities(),
        country="Algeria",
    )

    assert len(result) == 1
    assert result[0].name == "Albert Camus"


def test_filter_personalities_by_country_and_period():
    result = filter_personalities(
        _sample_personalities(),
        country="France",
        period="20th century",
    )

    assert len(result) == 2