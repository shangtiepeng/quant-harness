from __future__ import annotations

from packages.python.core.models import MarketOverview, StockSnapshot, StrategySignal
from packages.python.strategies.resonance import compute_resonance_score


def pick_leader_signals(
    stocks: list[StockSnapshot],
    market: MarketOverview,
    theme_heat: dict[str, dict[str, float | int | bool]],
    limit: int = 5,
) -> list[StrategySignal]:
    ranked = sorted(
        stocks,
        key=lambda s: (
            s.board_height * 25
            + s.auction_strength * 15
            + s.seal_strength * 15
            + s.turnover_rate * 2
            + s.narrative_score * 20
        ),
        reverse=True,
    )

    result: list[StrategySignal] = []
    for stock in ranked[:limit]:
        score = min(
            100,
            round(
                stock.board_height * 18
                + stock.auction_strength * 12
                + stock.seal_strength * 10
                + stock.turnover_rate * 1.5
                + stock.narrative_score * 20,
                1,
            ),
        )
        resonance_score, resonance_level, resonance_role, resonance_reasons = compute_resonance_score(
            stock,
            market,
            theme_heat,
        )
        result.append(
            StrategySignal(
                strategy="leader",
                symbol=stock.symbol,
                name=stock.name,
                score=score,
                risk_level="high" if stock.board_height >= 4 else "medium",
                reasons=[
                    f"连板高度 {stock.board_height}",
                    f"竞价强度 {stock.auction_strength}",
                    f"封单强度 {stock.seal_strength}",
                    f"题材归属 {stock.theme}",
                ],
                entry_note="关注分歧后的承接与回封，不追情绪极致一致。",
                exit_note="次日弱转强失败、放量走弱或核心题材退潮时考虑退出。",
                invalidation_note="若高开低走且失去板块带动性，则该信号失效。",
                theme=stock.theme,
                secondary_theme=stock.secondary_theme,
                concepts=stock.concepts,
                resonance_score=resonance_score,
                resonance_level=resonance_level,
                resonance_role=resonance_role,
                resonance_reasons=resonance_reasons,
            )
        )
    return result
