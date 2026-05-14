from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from political_spectrum_analyzer.domain.models import PersonalityPoint


def _parse_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"true", "1", "yes", "y"}


def _optional_str(value: str | None) -> str | None:
    cleaned = (value or "").strip()
    return cleaned or None


def _float_from_row(row: dict[str, str], key: str, default: float) -> float:
    value = row.get(key)

    if value is None or str(value).strip() == "":
        return default

    return float(value)


def load_personalities(csv_path: str | Path) -> List[PersonalityPoint]:
    csv_path = Path(csv_path)
    personalities: List[PersonalityPoint] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            personalities.append(
                PersonalityPoint(
                    name=row["name"].strip(),
                    display_group=row["display_group"].strip(),
                    x=float(row["x"]),
                    y=float(row["y"]),
                    ux=_float_from_row(row, "ux", 0.45),
                    uy=_float_from_row(row, "uy", 0.45),
                    confidence=(row.get("confidence") or "medium").strip().lower(),
                    is_estimated=_parse_bool(row.get("is_estimated")),
                    country=_optional_str(row.get("country")),
                    period=_optional_str(row.get("period")),
                    ideology_family=_optional_str(row.get("ideology_family")),
                    source=_optional_str(row.get("source")),
                    notes=_optional_str(row.get("notes")),
                )
            )

    return personalities