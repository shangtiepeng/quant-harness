from __future__ import annotations

from packages.python.data.real_collectors import load_market_data
from packages.python.reports.daily import build_daily_report
from packages.python.storage import save_pipeline_run
from packages.python.strategies.hotmoney import pick_hotmoney_signals
from packages.python.strategies.leader import pick_leader_signals
from packages.python.strategies.sentiment import compute_market_overview


def run_pipeline(limit: int = 50, persist: bool = False):
    stocks, meta = load_market_data(limit=limit)
    trade_date = meta["trade_date"]
    market = compute_market_overview(stocks, trade_date)
    leader_signals = pick_leader_signals(stocks, limit=5)
    hotmoney_signals = pick_hotmoney_signals(stocks, limit=5)
    signals = leader_signals + hotmoney_signals
    report = build_daily_report(trade_date, market, signals)

    payload = {
        "meta": meta,
        "trade_date": trade_date,
        "market": market.model_dump(),
        "signals": [s.model_dump() for s in signals],
        "report": report.model_dump(),
    }
    if persist:
        payload["run_id"] = save_pipeline_run(payload)
    return payload
