from pathlib import Path


def test_streamlit_metric_cards_have_readability_css():
    content = Path("src/political_spectrum_analyzer/streamlit_ui/styles.py").read_text(encoding="utf-8")

    assert "Make metric cards readable when values are long" in content
    assert 'div[data-testid="stMetricValue"]' in content
    assert "overflow-wrap: anywhere" in content
    assert "font-size: 1.42rem" in content
