from __future__ import annotations

from datetime import date
from random import Random
from typing import Any

from packages.python.storage import list_signals_by_run, save_validation


_rng = Random(42)


def _mock_returns(score: float) -> tuple[float, float, float]:
    bias = (score - 50) / 100
    r1 = round((_rng.uniform(-0.04, 0.07) + bias * 0.03) * 100, 2)
    r3 = round((_rng.uniform(-0.08, 0.12) + bias * 0.05) * 100, 2)
    r5 = round((_rng.uniform(-0.12, 0.18) + bias * 0.08) * 100, 2)
    return r1, r3, r5


def validate_run(run_id: int) -> list[dict[str, Any]]:
    signals = list_signals_by_run(run_id)
    results: list[dict[str, Any]] = []
    for signal in signals:
        r1, r3, r5 = _mock_returns(float(signal["score"]))
        if r1 >= 3:
            outcome = "strong"
        elif r1 >= 0:
            outcome = "neutral"
        else:
            outcome = "weak"

        payload = {
            "validation_date": str(date.today()),
            "return_1d": r1,
            "return_3d": r3,
            "return_5d": r5,
            "outcome_label": outcome,
            "note": "mock validation for closed-loop development; replace with real historical market follow-up later.",
        }
        validation_id = save_validation(int(signal["id"]), payload)
        results.append({"validation_id": validation_id, **signal, **payload})
    return results
