from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict

from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.services.text_import_service import extract_scores_from_text


DEBUG_OCR = os.getenv("DEBUG_OCR", "0") == "1"
DEBUG_DIR = Path("outputs") / "ocr_debug"

TESSERACT_EXE_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def _import_pytesseract() -> Any:
    """
    Import pytesseract lazily so the application can start without OCR dependencies.

    OCR is an optional feature. If pytesseract is missing, the error is raised only
    when the user explicitly tries to import a screenshot.
    """
    try:
        import pytesseract  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "OCR optional dependency is missing: pytesseract is not installed. "
            "Install it with: python -m pip install pytesseract"
        ) from exc

    return pytesseract


def _import_pillow() -> tuple[Any, Any, Any]:
    """
    Import Pillow lazily so the application can start even if OCR image dependencies
    are not installed.
    """
    try:
        from PIL import Image, ImageFilter, ImageOps  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "OCR optional dependency is missing: Pillow is not installed. "
            "Install it with: python -m pip install pillow"
        ) from exc

    return Image, ImageFilter, ImageOps


def _configure_tesseract(pytesseract_module: Any) -> None:
    """
    Ensure pytesseract can find the native Tesseract executable.

    On Windows, installing the Python package pytesseract is not enough.
    The native Tesseract OCR executable must also be installed.
    """
    if shutil.which("tesseract") is not None:
        return

    if Path(TESSERACT_EXE_PATH).exists():
        pytesseract_module.pytesseract.tesseract_cmd = TESSERACT_EXE_PATH
        return

    raise RuntimeError(
        "Tesseract OCR executable was not found. "
        "Install Tesseract OCR and add it to PATH, or update TESSERACT_EXE_PATH in "
        "src/political_spectrum_analyzer/ocr/politiscales_ocr.py. "
        f"Expected path: {TESSERACT_EXE_PATH}"
    )


def is_ocr_available() -> bool:
    """
    Return True if Python OCR dependencies and the native Tesseract executable are available.
    This is safe to call from the UI because it does not crash the application.
    """
    try:
        pytesseract_module = _import_pytesseract()
        _import_pillow()
        _configure_tesseract(pytesseract_module)
    except RuntimeError:
        return False

    return True


def _ensure_debug_dir() -> None:
    if DEBUG_OCR:
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)


def _save_debug_text(filename: str, content: str) -> None:
    if not DEBUG_OCR:
        return

    _ensure_debug_dir()
    (DEBUG_DIR / filename).write_text(content, encoding="utf-8")


def _save_debug_image(filename: str, image: Any) -> None:
    if not DEBUG_OCR:
        return

    _ensure_debug_dir()
    image.save(DEBUG_DIR / filename)


def _resize_image(image: Any, factor: int) -> Any:
    return image.resize((image.width * factor, image.height * factor))


def _preprocess_grayscale(image_path: str, factor: int = 3) -> Any:
    Image, ImageFilter, ImageOps = _import_pillow()

    image = Image.open(image_path).convert("L")
    image = ImageOps.autocontrast(image)
    image = _resize_image(image, factor)
    image = image.filter(ImageFilter.SHARPEN)

    return image


def _preprocess_threshold(image_path: str, factor: int = 3, threshold: int = 165) -> Any:
    image = _preprocess_grayscale(image_path, factor=factor)
    image = image.point(lambda p: 255 if p > threshold else 0)

    return image


def _preprocess_inverted(image_path: str, factor: int = 3) -> Any:
    _, ImageFilter, ImageOps = _import_pillow()

    image = _preprocess_grayscale(image_path, factor=factor)
    image = ImageOps.invert(image)
    image = image.filter(ImageFilter.SHARPEN)

    return image


def _count_detected_scores(scores: Dict[str, int]) -> int:
    return sum(1 for value in scores.values() if value != 0)


def _run_tesseract(image: Any, config: str) -> str:
    """
    Run Tesseract with French + English when available.
    Falls back to English if the French language pack is missing.
    """
    pytesseract_module = _import_pytesseract()
    _configure_tesseract(pytesseract_module)

    try:
        return pytesseract_module.image_to_string(image, lang="fra+eng", config=config)
    except pytesseract_module.TesseractError:
        return pytesseract_module.image_to_string(image, lang="eng", config=config)


def _evaluate_ocr_candidate(image: Any, config: str) -> tuple[str, Dict[str, int], int]:
    raw_text = _run_tesseract(image, config=config)
    scores = extract_scores_from_text(raw_text)
    detected_count = _count_detected_scores(scores)

    return raw_text, scores, detected_count


def extract_scores_from_image(image_path: str) -> Dict[str, int]:
    """
    OCR extraction for Politiscales screenshots.

    OCR is optional and non-blocking:
    - the application can start without pytesseract installed;
    - an explicit error is raised only when screenshot OCR is used without dependencies.

    Pipeline:
    1. Generate several preprocessed image variants.
    2. Run Tesseract with several page segmentation modes.
    3. Parse OCR text using the same parser as copied-text import.
    4. Keep the candidate with the highest number of detected scores.

    Notes:
    - OCR remains heuristic.
    - Manual review is still recommended after import.
    """
    preprocessors = [
        ("grayscale_x3", _preprocess_grayscale(image_path, factor=3)),
        ("threshold_x3_t150", _preprocess_threshold(image_path, factor=3, threshold=150)),
        ("threshold_x3_t165", _preprocess_threshold(image_path, factor=3, threshold=165)),
        ("threshold_x3_t180", _preprocess_threshold(image_path, factor=3, threshold=180)),
        ("inverted_x3", _preprocess_inverted(image_path, factor=3)),
    ]

    configs = [
        "--oem 3 --psm 6",
        "--oem 3 --psm 11",
        "--oem 3 --psm 4",
        "--oem 3 --psm 12",
    ]

    best_scores: Dict[str, int] = {name: 0 for name in VARIABLE_NAMES}
    best_text = ""
    best_detected_count = -1
    best_candidate_name = ""

    for image_name, image in preprocessors:
        _save_debug_image(f"{image_name}.png", image)

        for config in configs:
            raw_text, scores, detected_count = _evaluate_ocr_candidate(image, config)

            candidate_name = f"{image_name}_{config.replace(' ', '_').replace('-', '')}"

            _save_debug_text(
                f"{candidate_name}.txt",
                raw_text,
            )

            if detected_count > best_detected_count:
                best_detected_count = detected_count
                best_scores = scores
                best_text = raw_text
                best_candidate_name = candidate_name

            if detected_count == len(VARIABLE_NAMES):
                break

        if best_detected_count == len(VARIABLE_NAMES):
            break

    _save_debug_text(
        "best_ocr_candidate.txt",
        f"Best candidate: {best_candidate_name}\n"
        f"Detected scores: {best_detected_count}/{len(VARIABLE_NAMES)}\n\n"
        f"{best_text}",
    )

    return {name: best_scores.get(name, 0) for name in VARIABLE_NAMES}