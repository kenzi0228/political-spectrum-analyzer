from political_spectrum_analyzer.services.text_import_service import extract_scores_from_text


def test_extract_scores_from_text_detects_basic_scores():
    text = """
    Constructivisme 70%
    Essentialisme 30%
    Justice rehabilitative 65%
    Justice punitive 35%
    Progressisme 80%
    Conservatisme 20%
    Internationalisme 75%
    Nationalisme 25%
    Communisme 60%
    Capitalisme 40%
    Regulation 55%
    Laissez-faire 45%
    Ecologie 85%
    Productivisme 15%
    Revolution 50%
    Reformisme 50%
    """

    scores = extract_scores_from_text(text)

    assert scores["constructivisme"] == 70
    assert scores["essentialisme"] == 30
    assert scores["ecologie"] == 85
    assert scores["laissez_faire"] == 45