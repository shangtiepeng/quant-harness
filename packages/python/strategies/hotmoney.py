from __future__ import annotations

from packages.python.core.models import StockSnapshot, StrategySignal


def pick_hotmoney_signals(stocks: list[StockSnapshot], limit: int = 5) -> list[StrategySignal]:
    ranked = sorted(
        stocks,
        key=lambda s: (s.hot_money_net_buy_million, s.narrative_score, s.volume_ratio),
        reverse=True,
    )

    result: list[StrategySignal] = []
    for stock in ranked[:limit]:
        score = min(
            100,
            round(
                stock.hot_money_net_buy_million * 0.9
                + stock.narrative_score * 25
                + stock.volume_ratio * 10,
                1,
            ),
        )
        result.append(
            StrategySignal(
                strategy="hotmoney",
                symbol=stock.symbol,
                name=stock.name,
                score=score,
                risk_level="medium" if stock.hot_money_net_buy_million < 60 else "high",
                reasons=[
                    f"游资净买额 {stock.hot_money_net_buy_million} 百万",
                    f"量比 {stock.volume_ratio}",
                    f"叙事强度 {stock.narrative_score}",
                    f"题材归属 {stock.theme}",
                ],
                entry_note="优先关注与主线题材共振、且次日有承接预期的标的。",
                exit_note="若游资次日无溢价或板块分歧扩大，降低仓位或止盈。",
                invalidation_note="若席位行为与题材热度脱钩，则跟踪逻辑弱化。",
                theme=stock.theme,
            )
        )
    return result
