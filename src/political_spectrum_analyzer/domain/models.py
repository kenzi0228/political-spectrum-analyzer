from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class PersonalityPoint:
    name: str
    display_group: str
    x: float
    y: float
    ux: float = 0.45
    uy: float = 0.45
    is_estimated: bool = True
    source: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class PersonScores:
    name: str
    scores: Dict[str, int]


@dataclass(frozen=True)
class PersonResult:
    name: str
    scores: Dict[str, int]
    x: float
    y: float