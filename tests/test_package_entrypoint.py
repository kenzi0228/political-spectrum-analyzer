from political_spectrum_analyzer.cli import main


def test_cli_main_is_callable():
    assert callable(main)


def test_package_imports():
    import political_spectrum_analyzer

    assert political_spectrum_analyzer is not None