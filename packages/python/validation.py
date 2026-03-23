from __future__ import annotations

from datetime import date, datetime
from random import Random
from typing import Any

from packages.python.data.history_collectors import fetch_eastmoney_kline
from packages.python.storage import list_signals_by_run, save_validation


_rng = Random(42)


def _mock_returns(score: float) -> tuple[float, float, float]:
    bias = (score - 50) / 100
    r1 = round((_rng.uniform(-0.04, 0.07) + bias * 0.03) * 100, 2)
    r3 = round((_rng.uniform(-0.08, 0.12) + bias * 0.05) * 100, 2)
    r5 = round((_rng.uniform(-0.12, 0.18) + bias * 0.08) * 100, 2)
    return r1, r3, r5


def _compute_forward_returns(trade_date: str, rows: list[dict[str, Any]]) -> tuple[float | None, float | None, float | None]:
    if not rows:
        return None, None, None
    rows = sorted(rows, key=lambda x: x["date"])
    trade_dt = datetime.strptime(trade_date, "%Y-%m-%d").date()
    future = [r for r in rows if datetime.strptime(r["date"], "%Y-%m-%d").date() > trade_dt]
    if not future:
        return None, None, None

    base = future[0]["open"]

    def calc(idx: int) -> float | None:
        if len(future) <= idx:
            return None
        close = future[idx]["close"]
        return round((close / base - 1) * 100, 2)

    return calc(0), calc(2), calc(4)


def validate_run(run_id: int) -> list[dict[str, Any]]:
    signals = list_signals_by_run(run_id)
    results: list[dict[str, Any]] = []
    for signal in signals:
        note = "real_history"
        try:
            rows = fetch_eastmoney_kline(signal["symbol"], days=15)
            r1, r3, r5 = _compute_forward_returns(signal["trade_date"], rows)
            if r1 is None:
                raise ValueError("not enough future bars")
        except Exception:
            r1, r3, r5 = _mock_returns(float(signal["score"]))
            note = "mock_fallback"

        if (r1 or 0) >= 3:
            outcome = "strong"
        elif (r1 or 0) >= 0:
            outcome = "neutral"
        else:
            outcome = "weak"

        payload = {
            "validation_date": str(date.today()),
            "return_1d": r1,
            "return_3d": r3,
            "return_5d": r5,
            "outcome_label": outcome,
            "note": note,
        }
        validation_id = save_validation(int(signal["id"]), payload)
        results.append({"validation_id": validation_id, **signal, **payload})
    return results
