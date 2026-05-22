from pathlib import Path

from political_spectrum_analyzer.domain.models import PersonResult, PersonalityPoint
from political_spectrum_analyzer.services.export_results_service import build_export_rows
from political_spectrum_analyzer.web.plotly_plot import build_political_spectrum_figure


def test_streamlit_app_source_mentions_multi_profile_workflow():
    content = Path("streamlit_app.py").read_text(encoding="utf-8")
    text_content = Path("src/political_spectrum_analyzer/streamlit_ui/text.py").read_text(encoding="utf-8")
    input_content = Path("src/political_spectrum_analyzer/streamlit_ui/profile_inputs.py").read_text(encoding="utf-8")
    analysis_content = Path("src/political_spectrum_analyzer/streamlit_ui/analysis_rendering.py").read_text(encoding="utf-8")

    assert "_render_multi_profile_inputs" in content
    assert "profile_count_label" in text_content or "Number of profiles to compare" in text_content
    assert "analysis_multi_header" in analysis_content
    assert "Multi-profile analysis" in text_content
    assert "def render_multi_profile_inputs" in input_content


def test_plotly_figure_supports_multiple_people():
    people = [
        PersonResult(name="Profile A", scores={}, x=-1.0, y=0.5),
        PersonResult(name="Profile B", scores={}, x=1.2, y=-0.7),
    ]

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
        people=people,
        personalities=[reference],
    )

    assert fig is not None
    assert len(fig.data) == 2
    assert len(fig.data[1].x) == 2


def test_export_rows_support_multiple_profiles():
    people = [
        PersonResult(name="Profile A", scores={}, x=-1.0, y=0.5),
        PersonResult(name="Profile B", scores={}, x=1.2, y=-0.7),
    ]

    references = [
        PersonalityPoint(
            name="Reference",
            display_group="Test",
            country="France",
            period="20th century",
            ideology_family="Liberalism",
            x=-1.2,
            y=0.4,
        )
    ]

    rows = build_export_rows(
        people=people,
        personalities=references,
        mode="profiles_only",
    )

    assert len(rows) == 2
    assert rows[0]["profile_name"] == "Profile A"
    assert rows[1]["profile_name"] == "Profile B"
