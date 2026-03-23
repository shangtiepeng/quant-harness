from __future__ import annotations

from packages.python.core.models import DailyReport, MarketOverview, StrategySignal


def build_daily_report(
    trade_date: str,
    market: MarketOverview,
    signals: list[StrategySignal],
) -> DailyReport:
    top = sorted(signals, key=lambda s: s.score, reverse=True)[:8]
    names = "、".join(f"{s.name}({s.symbol})" for s in top[:5]) if top else "无"

    summary_cn = (
        f"{trade_date} 市场情绪阶段为 {market.market_sentiment_stage}。"
        f"涨停 {market.limit_up_count} 家，跌停 {market.limit_down_count} 家，最高连板 {market.highest_board}。"
        f"当前值得重点观察的标的包括：{names}。"
        "建议先以盘后研究和次日验证为主，谨慎直接自动执行。"
    )

    summary_en = (
        f"On {trade_date}, the market sentiment stage is {market.market_sentiment_stage}. "
        f"There are {market.limit_up_count} limit-up stocks, {market.limit_down_count} limit-down stocks, "
        f"and the highest board is {market.highest_board}. "
        f"Key watchlist names: {names}. "
        "Use this as a research-first signal report rather than a fully automated execution trigger."
    )

    return DailyReport(
        trade_date=trade_date,
        market=market,
        top_signals=top,
        summary_cn=summary_cn,
        summary_en=summary_en,
    )
