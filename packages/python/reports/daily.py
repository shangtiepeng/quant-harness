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

    unique_top = unique_by_symbol(top)
    focus = [s for s in unique_top if s.resonance_level in {'A', 'B'}][:3]
    observe = [s for s in unique_top if s.resonance_level == 'C'][:3]
    avoid = [s for s in unique_top if s.resonance_level == 'D'][:2]

    theme_seen: set[str] = set()
    mainline_themes: list[str] = []
    for signal in unique_top:
        if signal.theme and signal.theme != '题材待补全' and signal.theme not in theme_seen:
            theme_seen.add(signal.theme)
            mainline_themes.append(signal.theme)
        if len(mainline_themes) >= 3:
            break

    focus_names = [f"{s.name}({s.symbol})" for s in focus]
    observe_names = [f"{s.name}({s.symbol})" for s in observe]
    avoid_names = [f"{s.name}({s.symbol})" for s in avoid]

    focus_cn = '、'.join(focus_names) if focus_names else '暂无强共振标的'
    avoid_cn = '、'.join(avoid_names) if avoid_names else '暂无明显回避标的'

    tomorrow_plan: list[str] = []
    stage_cn = STAGE_CN.get(market.market_sentiment_stage, market.market_sentiment_stage)
    if mainline_themes:
        tomorrow_plan.append(f"优先盯住主线题材：{'、'.join(mainline_themes[:2])}。")
    if focus_names:
        tomorrow_plan.append(f"重点跟踪强共振候选的竞价、承接和回封质量：{'、'.join(focus_names[:2])}。")
    if market.market_sentiment_stage == 'ice':
        tomorrow_plan.append('情绪仍偏冰点，适合轻仓试错，不宜把弱共振信号当成进攻主仓。')
    elif market.market_sentiment_stage == 'repair':
        tomorrow_plan.append('若修复延续，优先看主线前排而非后排补涨。')
    elif market.market_sentiment_stage == 'hot':
        tomorrow_plan.append('若情绪高潮延续，注意一致性过强后的次日分歧风险。')
    else:
        tomorrow_plan.append('若盘中分歧扩大，优先保留强共振核心，回避纯跟风。')

    summary_cn = (
        f"{trade_date} 市场处于{stage_cn}阶段，"
        f"涨停 {market.limit_up_count} 家，跌停 {market.limit_down_count} 家，最高连板 {market.highest_board}。"
        f"当前优先关注强共振候选：{focus_cn}。"
        f"其中优先看主线题材内的主线龙头/前排核心，弱共振或噪声信号如 {avoid_cn} 更适合观察而非追击。"
        "整体仍以盘后研究、次日验证和轻量试错为主，不建议直接当作全自动执行信号。"
    )

    summary_en = (
        f"On {trade_date}, the market is in {market.market_sentiment_stage} stage. "
        f"There are {market.limit_up_count} limit-up stocks, {market.limit_down_count} limit-down stocks, "
        f"and the highest board is {market.highest_board}. "
        f"Priority goes to high-resonance names: {focus_cn}. "
        f"Prefer mainline leaders/frontline core setups, while weaker names such as {avoid_cn} are better treated as watch-only. "
        "Use this as a research and next-day validation framework, not a fully automated execution trigger."
    )

    return DailyReport(
        trade_date=trade_date,
        market=market,
        top_signals=top,
        summary_cn=summary_cn,
        summary_en=summary_en,
        mainline_themes=mainline_themes,
        focus_candidates=focus_names,
        observe_candidates=observe_names,
        avoid_candidates=avoid_names,
        tomorrow_plan=tomorrow_plan,
    )
