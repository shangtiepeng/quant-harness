from __future__ import annotations

from collections import Counter

from packages.python.core.models import MarketOverview, StockSnapshot


def build_theme_heat_map(stocks: list[StockSnapshot]) -> dict[str, dict[str, float | int | bool]]:
    counter: Counter[str] = Counter()
    score_map: dict[str, float] = {}
    for stock in stocks:
        concepts = stock.concepts or ([stock.theme] if stock.theme else [])
        for idx, concept in enumerate(concepts[:3]):
            if not concept or concept == '题材待补全':
                continue
            weight = 1.0 if idx == 0 else 0.6 if idx == 1 else 0.3
            counter[concept] += 1
            score_map[concept] = score_map.get(concept, 0.0) + (
                weight * (1 + max(stock.pct_change, 0) / 10 + stock.volume_ratio / 5)
            )

    ranked = sorted(counter.items(), key=lambda item: (score_map.get(item[0], 0), item[1]), reverse=True)
    mainline_themes = {theme for idx, (theme, _count) in enumerate(ranked[:3]) if idx < 3}

    heat_map: dict[str, dict[str, float | int | bool]] = {}
    for rank, (theme, count) in enumerate(ranked, start=1):
        heat_map[theme] = {
            'rank': rank,
            'count': count,
            'heat_score': round(score_map.get(theme, 0.0), 2),
            'is_mainline': theme in mainline_themes,
        }
    return heat_map


def market_stage_score(stage: str) -> float:
    mapping = {
        'ice': 45.0,
        'repair': 65.0,
        'split': 55.0,
        'hot': 75.0,
    }
    return mapping.get(stage, 50.0)


def classify_resonance_role(
    stock: StockSnapshot,
    market: MarketOverview,
    theme_heat: dict[str, dict[str, float | int | bool]],
) -> str:
    theme_info = theme_heat.get(stock.theme, {})
    is_mainline = bool(theme_info.get('is_mainline', False))
    board_height = stock.board_height
    strength = stock.auction_strength + stock.seal_strength + stock.narrative_score

    if is_mainline and (board_height >= 2 or strength >= 2.2):
        return 'mainline_leader'
    if is_mainline and strength >= 1.6:
        return 'frontline_core'
    if not is_mainline and market.market_sentiment_stage in {'repair', 'hot'} and stock.narrative_score >= 0.7:
        return 'secondary_rotation'
    if stock.volume_ratio >= 2.0 or stock.hot_money_net_buy_million >= 20:
        return 'follower'
    return 'noise'


def compute_resonance_score(
    stock: StockSnapshot,
    market: MarketOverview,
    theme_heat: dict[str, dict[str, float | int | bool]],
) -> tuple[float, str, str, list[str]]:
    theme_info = theme_heat.get(stock.theme, {})
    is_mainline = bool(theme_info.get('is_mainline', False))
    theme_rank = int(theme_info.get('rank', 99) or 99)
    theme_score = float(theme_info.get('heat_score', 0.0) or 0.0)

    score = 0.0
    score += market_stage_score(market.market_sentiment_stage) * 0.18
    score += min(theme_score * 3.2, 24)
    score += 12 if is_mainline else max(0, 8 - min(theme_rank, 8))
    score += min(stock.board_height * 8, 16)
    score += min(stock.auction_strength * 8, 8)
    score += min(stock.seal_strength * 8, 8)
    score += min(stock.narrative_score * 14, 14)
    score += min(stock.volume_ratio * 3.5, 10)
    score += min(stock.turnover_rate * 0.8, 10)
    score += min(max(stock.hot_money_net_buy_million, 0) * 0.18, 10)

    role = classify_resonance_role(stock, market, theme_heat)
    if role == 'mainline_leader':
        score += 8
    elif role == 'frontline_core':
        score += 5
    elif role == 'secondary_rotation':
        score += 2
    elif role == 'noise':
        score -= 8

    score = max(0.0, min(100.0, round(score, 1)))

    if score >= 78:
        level = 'A'
    elif score >= 64:
        level = 'B'
    elif score >= 50:
        level = 'C'
    else:
        level = 'D'

    reasons = [
        f"情绪阶段 {market.market_sentiment_stage}",
        f"题材热度排名 {theme_rank if theme_rank < 99 else '未上榜'}",
        f"题材热度分 {theme_score}",
        f"共振角色 {role}",
    ]
    if is_mainline:
        reasons.append('属于当前主线题材')
    if stock.hot_money_net_buy_million > 0:
        reasons.append(f"游资净买额 {stock.hot_money_net_buy_million} 百万")

    return score, level, role, reasons
