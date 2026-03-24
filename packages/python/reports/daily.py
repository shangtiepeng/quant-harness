from __future__ import annotations

from packages.python.core.models import DailyReport, MarketOverview, StrategySignal


STAGE_CN = {
    'ice': '冰点',
    'repair': '修复',
    'split': '分歧',
    'hot': '高潮',
}

ROLE_CN = {
    'mainline_leader': '主线龙头',
    'frontline_core': '前排核心',
    'secondary_rotation': '轮动补涨',
    'follower': '跟风观察',
    'noise': '噪声票',
}


def build_daily_report(
    trade_date: str,
    market: MarketOverview,
    signals: list[StrategySignal],
) -> DailyReport:
    top = sorted(signals, key=lambda s: (s.resonance_score, s.score), reverse=True)[:8]

    def unique_by_symbol(items: list[StrategySignal]) -> list[StrategySignal]:
        result: list[StrategySignal] = []
        seen: set[str] = set()
        for item in items:
            if item.symbol in seen:
                continue
            seen.add(item.symbol)
            result.append(item)
        return result

    focus = unique_by_symbol([s for s in top if s.resonance_level in {'A', 'B'}])[:3]
    avoid = unique_by_symbol([s for s in top if s.resonance_level in {'C', 'D'}])[:2]

    focus_names = '、'.join(f"{s.name}({s.symbol})" for s in focus) if focus else '暂无强共振标的'
    avoid_names = '、'.join(f"{s.name}({s.symbol})" for s in avoid) if avoid else '暂无明显回避标的'

    summary_cn = (
        f"{trade_date} 市场处于{STAGE_CN.get(market.market_sentiment_stage, market.market_sentiment_stage)}阶段，"
        f"涨停 {market.limit_up_count} 家，跌停 {market.limit_down_count} 家，最高连板 {market.highest_board}。"
        f"当前优先关注强共振候选：{focus_names}。"
        f"其中优先看主线题材内的主线龙头/前排核心，弱共振或噪声信号如 {avoid_names} 更适合观察而非追击。"
        "整体仍以盘后研究、次日验证和轻量试错为主，不建议直接当作全自动执行信号。"
    )

    summary_en = (
        f"On {trade_date}, the market is in {market.market_sentiment_stage} stage. "
        f"There are {market.limit_up_count} limit-up stocks, {market.limit_down_count} limit-down stocks, "
        f"and the highest board is {market.highest_board}. "
        f"Priority goes to high-resonance names: {focus_names}. "
        f"Prefer mainline leaders/frontline core setups, while weaker names such as {avoid_names} are better treated as watch-only. "
        "Use this as a research and next-day validation framework, not a fully automated execution trigger."
    )

    return DailyReport(
        trade_date=trade_date,
        market=market,
        top_signals=top,
        summary_cn=summary_cn,
        summary_en=summary_en,
    )
