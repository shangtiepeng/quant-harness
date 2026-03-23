from __future__ import annotations

from datetime import date

from packages.python.data.sample_loader import load_sample_market
from packages.python.reports.daily import build_daily_report
from packages.python.strategies.hotmoney import pick_hotmoney_signals
from packages.python.strategies.leader import pick_leader_signals
from packages.python.strategies.sentiment import compute_market_overview


def run_pipeline():
    trade_date = str(date.today())
    stocks = load_sample_market()
    market = compute_market_overview(stocks, trade_date)
    leader_signals = pick_leader_signals(stocks, limit=5)
    hotmoney_signals = pick_hotmoney_signals(stocks, limit=5)
    signals = leader_signals + hotmoney_signals
    report = build_daily_report(trade_date, market, signals)

    return {
        "trade_date": trade_date,
        "market": market.model_dump(),
        "signals": [s.model_dump() for s in signals],
        "report": report.model_dump(),
    }
