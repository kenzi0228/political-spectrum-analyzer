from __future__ import annotations

import csv
from pathlib import Path
from typing import List

from political_spectrum_analyzer.domain.models import PersonalityPoint


def _parse_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"true", "1", "yes", "y"}


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
                    ux=float(row.get("ux", 0.45) or 0.45),
                    uy=float(row.get("uy", 0.45) or 0.45),
                    is_estimated=_parse_bool(row.get("is_estimated")),
                    source=(row.get("source") or "").strip() or None,
                    notes=(row.get("notes") or "").strip() or None,
                )
            )

    return personalities