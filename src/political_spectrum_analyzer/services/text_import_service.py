from __future__ import annotations

import re
import unicodedata

from political_spectrum_analyzer.constants import VARIABLE_NAMES


POLITISCALES_PAIRS = [
    ("constructivisme", "essentialisme"),
    ("justice_rehabilitative", "justice_punitive"),
    ("progressisme", "conservatisme"),
    ("internationalisme", "nationalisme"),
    ("communisme", "capitalisme"),
    ("regulation", "laissez_faire"),
    ("ecologie", "productivisme"),
    ("revolution", "reformisme"),
]


LABEL_ALIASES = {
    "constructivisme": ["constructivisme", "constructivism"],
    "essentialisme": ["essentialisme", "essentialism"],
    "justice_rehabilitative": ["justice rehabilitative", "justice réhabilitative", "rehabilitative justice"],
    "justice_punitive": ["justice punitive", "punitive justice"],
    "progressisme": ["progressisme", "progressivism"],
    "conservatisme": ["conservatisme", "conservatism"],
    "internationalisme": ["internationalisme", "internationalism"],
    "nationalisme": ["nationalisme", "nationalism"],
    "communisme": ["communisme", "communism"],
    "capitalisme": ["capitalisme", "capitalism"],
    "regulation": ["regulation", "régulation", "regulationnisme", "regulationism"],
    "laissez_faire": ["laissez faire", "laissez-faire"],
    "ecologie": ["ecologie", "écologie", "ecology"],
    "productivisme": ["productivisme", "productivism"],
    "revolution": ["revolution", "révolution"],
    "reformisme": ["reformisme", "réformisme", "reformism"],
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
    text = re.sub(r"[·•]", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _normalize_line(line: str) -> str:
    return normalize_text(line).strip()


def _is_percentage_line(line: str) -> bool:
    return re.fullmatch(r"\d{1,3}\s*%?", line.strip()) is not None


def _extract_percentage(line: str) -> int | None:
    match = re.search(r"\b(\d{1,3})\s*%?", line.strip())
    if not match:
        return None

    value = int(match.group(1))
    if 0 <= value <= 100:
        return value

    return None


def _is_label_line(line: str, variable_name: str) -> bool:
    normalized = _normalize_line(line)

    for alias in LABEL_ALIASES[variable_name]:
        if normalized == _normalize_line(alias):
            return True

    return False


def _detect_label(line: str) -> str | None:
    for variable_name in VARIABLE_NAMES:
        if _is_label_line(line, variable_name):
            return variable_name

    return None


def _clean_lines(raw_text: str) -> list[str]:
    lines = []

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if line:
            lines.append(line)

    return lines


def _parse_politiscales_pair_format(raw_text: str) -> dict[str, int]:
    """
    Parse real Politiscales copied text.

    Expected structure:
        Label A
        Label B
        A%
        neutral%
        B%

    Rule:
        - first percentage = first label
        - last percentage = second label
        - middle percentage, if present, is ignored
    """
    lines = _clean_lines(raw_text)
    scores: dict[str, int] = {}

    i = 0
    while i < len(lines) - 1:
        current_label = _detect_label(lines[i])
        next_label = _detect_label(lines[i + 1])

        if current_label is None or next_label is None:
            i += 1
            continue

        if (current_label, next_label) not in POLITISCALES_PAIRS:
            i += 1
            continue

        percentages: list[int] = []
        j = i + 2

        while j < len(lines):
            detected_label = _detect_label(lines[j])

            if detected_label is not None:
                break

            if _is_percentage_line(lines[j]):
                value = _extract_percentage(lines[j])
                if value is not None:
                    percentages.append(value)

            j += 1

        if len(percentages) >= 2:
            scores[current_label] = percentages[0]
            scores[next_label] = percentages[-1]

        i = j

    return scores


def _find_inline_score(raw_text: str, variable_name: str) -> int | None:
    """
    Fallback for simple formats like:
        Constructivisme 70%
        Essentialisme 30%
    """
    text = normalize_text(raw_text)

    aliases = [_normalize_line(alias) for alias in LABEL_ALIASES[variable_name]]
    alias_pattern = r"(?:%s)" % "|".join(re.escape(alias) for alias in aliases)

    patterns = [
        rf"{alias_pattern}\D{{0,40}}(\d{{1,3}})\s*%",
        rf"(\d{{1,3}})\s*%\D{{0,40}}{alias_pattern}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            value = int(match.group(1))
            if 0 <= value <= 100:
                return value

    return None


def _parse_inline_format(raw_text: str) -> dict[str, int]:
    scores: dict[str, int] = {}

    for variable_name in VARIABLE_NAMES:
        value = _find_inline_score(raw_text, variable_name)
        if value is not None:
            scores[variable_name] = value

    return scores


def extract_scores_from_text(raw_text: str) -> dict[str, int]:
    """
    Extract Politiscales scores from copied text.

    Priority:
    1. Real Politiscales pair format.
    2. Simple inline fallback format.
    """
    scores: dict[str, int] = {name: 0 for name in VARIABLE_NAMES}

    pair_scores = _parse_politiscales_pair_format(raw_text)
    inline_scores = _parse_inline_format(raw_text)

    for variable_name in VARIABLE_NAMES:
        if variable_name in pair_scores:
            scores[variable_name] = pair_scores[variable_name]
        elif variable_name in inline_scores:
            scores[variable_name] = inline_scores[variable_name]

    return scores