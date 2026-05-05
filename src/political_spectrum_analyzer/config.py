from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
REFERENCE_DATA_DIR = DATA_DIR / "reference"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

PERSONALITIES_CSV_PATH = REFERENCE_DATA_DIR / "personalities.csv"