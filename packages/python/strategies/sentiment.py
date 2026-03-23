from __future__ import annotations

from packages.python.core.models import MarketOverview, StockSnapshot


def compute_market_overview(stocks: list[StockSnapshot], trade_date: str) -> MarketOverview:
    limit_up_count = sum(1 for s in stocks if s.is_limit_up)
    limit_down_count = sum(1 for s in stocks if s.pct_change <= -9)
    broken_count = sum(1 for s in stocks if s.is_broken_board)
    highest_board = max((s.board_height for s in stocks), default=0)
    broken_rate = round(broken_count / max(limit_up_count + broken_count, 1), 3)

    if limit_up_count <= 20 or highest_board <= 2:
        stage = "ice"
    elif broken_rate < 0.18 and highest_board >= 4:
        stage = "hot"
    elif broken_rate < 0.35:
        stage = "repair"
    else:
        stage = "split"

    notes = [
        f"涨停家数 {limit_up_count} / Limit-up count {limit_up_count}",
        f"跌停家数 {limit_down_count} / Limit-down count {limit_down_count}",
        f"最高连板 {highest_board} / Highest board {highest_board}",
        f"炸板率 {broken_rate:.1%} / Broken-board rate {broken_rate:.1%}",
    ]

    return MarketOverview(
        trade_date=trade_date,
        market_sentiment_stage=stage,
        limit_up_count=limit_up_count,
        limit_down_count=limit_down_count,
        broken_board_rate=broken_rate,
        highest_board=highest_board,
        notes=notes,
    )
