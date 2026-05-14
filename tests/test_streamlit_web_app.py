from political_spectrum_analyzer.domain.models import PersonResult, PersonalityPoint
from political_spectrum_analyzer.web.plotly_plot import build_political_spectrum_figure


def test_build_political_spectrum_figure_returns_plotly_figure():
    person = PersonResult(
        name="Test profile",
        scores={},
        x=-1.0,
        y=0.5,
    )

    reference = PersonalityPoint(
        name="Reference",
        display_group="Test",
        country="France",
        period="20th century",
        ideology_family="Liberalism",
        x=-1.2,
        y=0.4,
    )

    fig = build_political_spectrum_figure(
        people=[person],
        personalities=[reference],
    )

    assert fig is not None
    assert len(fig.data) == 2