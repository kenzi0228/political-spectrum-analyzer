def test_ocr_module_imports_without_eager_tesseract_dependency():
    from political_spectrum_analyzer.ocr import extract_scores_from_image, is_ocr_available

    assert callable(extract_scores_from_image)
    assert callable(is_ocr_available)


def test_application_imports_without_running_ocr():
    from political_spectrum_analyzer.ui.app import WizardApp

    assert WizardApp is not None