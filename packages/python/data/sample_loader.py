from __future__ import annotations

import json
from pathlib import Path
from packages.python.core.models import StockSnapshot


ROOT = Path(__file__).resolve().parents[3]
SAMPLE_FILE = ROOT / "data" / "sample" / "market_sample.json"


def load_sample_market() -> list[StockSnapshot]:
    raw = json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))
    return [StockSnapshot(**item) for item in raw]
