from __future__ import annotations

import re
from typing import Dict

import pytesseract
from PIL import Image, ImageOps, ImageFilter

from political_spectrum_analyzer.constants import VARIABLE_NAMES


ALIASES = {
    "constructivisme": ["constructivisme", "constructivism"],
    "essentialisme": ["essentialisme", "essentialism"],
    "justice_rehabilitative": ["justice rehabilitative", "rehabilitative justice"],
    "justice_punitive": ["justice punitive", "punitive justice"],
    "progressisme": ["progressisme", "progressivism"],
    "conservatisme": ["conservatisme", "conservatism"],
    "internationalisme": ["internationalisme", "internationalism"],
    "nationalisme": ["nationalisme", "nationalism"],
    "communisme": ["communisme", "communism"],
    "capitalisme": ["capitalisme", "capitalism"],
    "regulation": ["regulation", "regulationnisme", "regulationism"],
    "laissez_faire": ["laissez faire", "laissez-faire"],
    "ecologie": ["ecologie", "ecology"],
    "productivisme": ["productivisme", "productivism"],
    "revolution": ["revolution"],
    "reformisme": ["reformisme", "reformism"],
}


def _normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("’", "'")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    return text


def _preprocess_image(image_path: str) -> Image.Image:
    image = Image.open(image_path).convert("L")
    image = ImageOps.autocontrast(image)
    image = image.resize((image.width * 2, image.height * 2))
    image = image.filter(ImageFilter.SHARPEN)

    # Simple threshold
    image = image.point(lambda p: 255 if p > 160 else 0)
    return image


def _extract_percentage_candidates(text: str) -> list[int]:
    return [int(x) for x in re.findall(r"\b(\d{1,3})\s*%", text) if 0 <= int(x) <= 100]


def _find_score_for_alias(text: str, alias: str) -> int | None:
    """
    Try to find a percentage near a given alias.
    """
    alias_pattern = re.escape(alias)
    patterns = [
        rf"{alias_pattern}.{{0,40}}?(\d{{1,3}})\s*%",
        rf"(\d{{1,3}})\s*%.{{0,40}}?{alias_pattern}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            value = int(match.group(1))
            if 0 <= value <= 100:
                return value

    return None


def extract_scores_from_image(image_path: str) -> Dict[str, int]:
    """
    OCR extraction for Politiscales screenshots.
    Returns a dict containing the 16 variables.

    Notes:
    - OCR is heuristic and may require manual correction.
    - Missing variables default to 0.
    """
    processed_image = _preprocess_image(image_path)

    raw_text = pytesseract.image_to_string(processed_image, lang="eng")
    text = _normalize_text(raw_text)

    scores: Dict[str, int] = {name: 0 for name in VARIABLE_NAMES}

    for variable_name, aliases in ALIASES.items():
        for alias in aliases:
            value = _find_score_for_alias(text, alias)
            if value is not None:
                scores[variable_name] = value
                break
    return scores