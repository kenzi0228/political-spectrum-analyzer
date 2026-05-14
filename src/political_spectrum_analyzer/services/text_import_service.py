from __future__ import annotations

import re
import unicodedata

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


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def normalize_text(text: str) -> str:
    text = text.lower()
    text = _strip_accents(text)
    text = text.replace("’", "'")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("_", " ")
    return text


def _find_score_for_alias(text: str, alias: str) -> int | None:
    alias = normalize_text(alias)
    alias_pattern = re.escape(alias)

    patterns = [
        rf"{alias_pattern}\D{{0,80}}(\d{{1,3}})\s*%?",
        rf"(\d{{1,3}})\s*%?\D{{0,80}}{alias_pattern}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            value = int(match.group(1))
            if 0 <= value <= 100:
                return value

    return None


def extract_scores_from_text(raw_text: str) -> dict[str, int]:
    text = normalize_text(raw_text)
    scores: dict[str, int] = {name: 0 for name in VARIABLE_NAMES}

    for variable_name, aliases in ALIASES.items():
        for alias in aliases:
            value = _find_score_for_alias(text, alias)
            if value is not None:
                scores[variable_name] = value
                break

    return scores
