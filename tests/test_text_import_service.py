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
    Reformism 50%
    """

    scores = extract_scores_from_text(text)

    assert scores["constructivisme"] == 70
    assert scores["essentialisme"] == 30
    assert scores["ecologie"] == 85
    assert scores["laissez_faire"] == 45


def test_extract_scores_from_politiscales_pair_format():
    text = """
    PolitiScales

    politiscales.fr

    Patrie . Travail · Liberté

    Constructivisme

    Essentialisme

    7%

    26%

    67%

    Justice réhabilitative

    Justice punitive

    24%

    71%

    Progressisme

    Conservatisme

    36%

    19%

    45%

    Internationalisme

    Nationalisme

    10%
    90%

    Communisme

    Capitalisme

    17%

    16%

    67%

    Régulation

    Laissez-faire

    29%

    26%

    45%

    Écologie

    Productivisme

    17%

    35%

    48%

    Révolution

    Réformisme

    38%

    33%

    29%

    149-462
    """

    scores = extract_scores_from_text(text)

    assert scores["constructivisme"] == 7
    assert scores["essentialisme"] == 67

    assert scores["justice_rehabilitative"] == 24
    assert scores["justice_punitive"] == 71

    assert scores["progressisme"] == 36
    assert scores["conservatisme"] == 45

    assert scores["internationalisme"] == 10
    assert scores["nationalisme"] == 90

    assert scores["communisme"] == 17
    assert scores["capitalisme"] == 67

    assert scores["regulation"] == 29
    assert scores["laissez_faire"] == 45

    assert scores["ecologie"] == 17
    assert scores["productivisme"] == 48

    assert scores["revolution"] == 38
    assert scores["reformisme"] == 29