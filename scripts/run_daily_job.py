#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from packages.python.daily_jobs import run_daily_job


if __name__ == "__main__":
    result = run_daily_job()
    print(json.dumps(result, ensure_ascii=False, indent=2))
