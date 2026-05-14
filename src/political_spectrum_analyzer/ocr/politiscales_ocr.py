from __future__ import annotations

from pathlib import Path
from typing import Dict

import pytesseract
from PIL import Image, ImageFilter, ImageOps

from political_spectrum_analyzer.constants import VARIABLE_NAMES
from political_spectrum_analyzer.services.text_import_service import extract_scores_from_text


DEBUG_OCR = True
DEBUG_DIR = Path("outputs") / "ocr_debug"


def _ensure_debug_dir() -> None:
    if DEBUG_OCR:
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)


def _save_debug_text(filename: str, content: str) -> None:
    if not DEBUG_OCR:
        return

    _ensure_debug_dir()
    (DEBUG_DIR / filename).write_text(content, encoding="utf-8")


def _save_debug_image(filename: str, image: Image.Image) -> None:
    if not DEBUG_OCR:
        return

    _ensure_debug_dir()
    image.save(DEBUG_DIR / filename)


def _resize_image(image: Image.Image, factor: int) -> Image.Image:
    return image.resize((image.width * factor, image.height * factor))


def _preprocess_grayscale(image_path: str, factor: int = 3) -> Image.Image:
    image = Image.open(image_path).convert("L")
    image = ImageOps.autocontrast(image)
    image = _resize_image(image, factor)
    image = image.filter(ImageFilter.SHARPEN)
    return image


def _preprocess_threshold(image_path: str, factor: int = 3, threshold: int = 165) -> Image.Image:
    image = _preprocess_grayscale(image_path, factor=factor)
    image = image.point(lambda p: 255 if p > threshold else 0)
    return image


def _preprocess_inverted(image_path: str, factor: int = 3) -> Image.Image:
    image = _preprocess_grayscale(image_path, factor=factor)
    image = ImageOps.invert(image)
    image = image.filter(ImageFilter.SHARPEN)
    return image


def _count_detected_scores(scores: Dict[str, int]) -> int:
    return sum(1 for value in scores.values() if value != 0)


def _run_tesseract(image: Image.Image, config: str) -> str:
    """
    Runs Tesseract with French + English when available.
    Falls back to English if the French language pack is missing.
    """
    try:
        return pytesseract.image_to_string(image, lang="fra+eng", config=config)
    except pytesseract.TesseractError:
        return pytesseract.image_to_string(image, lang="eng", config=config)


def _evaluate_ocr_candidate(image: Image.Image, config: str) -> tuple[str, Dict[str, int], int]:
    raw_text = _run_tesseract(image, config=config)
    scores = extract_scores_from_text(raw_text)
    detected_count = _count_detected_scores(scores)

    return raw_text, scores, detected_count


def extract_scores_from_image(image_path: str) -> Dict[str, int]:
    """
    OCR extraction for Politiscales screenshots.

    Pipeline:
    1. Generate several preprocessed image variants.
    2. Run Tesseract with several page segmentation modes.
    3. Parse the OCR text using the same parser as copied-text import.
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