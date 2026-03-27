from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from packages.python.backtest import backtest_signals
from packages.python.strategy_governor import build_strategy_governor


RISK_MODE_LIMITS: dict[str, dict[str, float]] = {
    'defensive_probe': {
        'single_position_cap_pct': 8.0,
        'single_theme_cap_pct': 12.0,
        'single_strategy_cap_pct': 14.0,
        'daily_new_exposure_cap_pct': 20.0,
    },
    'risk_control': {
        'single_position_cap_pct': 10.0,
        'single_theme_cap_pct': 15.0,
        'single_strategy_cap_pct': 18.0,
        'daily_new_exposure_cap_pct': 30.0,
    },
    'selective_attack': {
        'single_position_cap_pct': 14.0,
        'single_theme_cap_pct': 20.0,
        'single_strategy_cap_pct': 26.0,
        'daily_new_exposure_cap_pct': 45.0,
    },
    'active_attack': {
        'single_position_cap_pct': 18.0,
        'single_theme_cap_pct': 25.0,
        'single_strategy_cap_pct': 35.0,
        'daily_new_exposure_cap_pct': 60.0,
    },
}


def _bucket_avg_return(items: list[dict[str, Any]], key: str, value: str) -> float | None:
    subset = [x for x in items if str(x.get(key) or '') == value and x.get('return_1d') is not None]
    if not subset:
        return None
    return round(mean(float(x['return_1d']) for x in subset), 2)


def _bucket_win_rate(items: list[dict[str, Any]], key: str, value: str) -> float | None:
    subset = [x for x in items if str(x.get(key) or '') == value and x.get('return_1d') is not None]
    if not subset:
        return None
    wins = sum(1 for x in subset if float(x['return_1d']) > 0)
    return round(wins / len(subset) * 100, 2)


def build_risk_profile(market: dict[str, Any], candidate_plan: list[dict[str, Any]], history_limit: int = 200) -> dict[str, Any]:
    risk_mode = str(market.get('risk_mode') or 'defensive_probe')
    market_stage = str(market.get('market_stage') or market.get('market_sentiment_stage') or 'ice')
    limits = dict(RISK_MODE_LIMITS.get(risk_mode, RISK_MODE_LIMITS['defensive_probe']))

    backtest = backtest_signals(limit=history_limit, kline_days=60)
    historical_trades = backtest.get('trades') or []
    strategy_governor = build_strategy_governor(history_limit=history_limit)

    stage_avg = _bucket_avg_return(historical_trades, 'market_stage', market_stage)
    stage_win_rate = _bucket_win_rate(historical_trades, 'market_stage', market_stage)

    recent_negative_streak = 0
    recent_trades = sorted(
        [t for t in historical_trades if t.get('return_1d') is not None],
        key=lambda x: (x.get('trade_date') or '', int(x.get('signal_id') or 0)),
        reverse=True,
    )[:12]
    for item in recent_trades:
        if float(item.get('return_1d') or 0) <= 0:
            recent_negative_streak += 1
        else:
            break

    cooldown = recent_negative_streak >= 4 or (stage_avg is not None and stage_avg < -1.5)
    risk_discount = 1.0
    notes: list[str] = []
    if stage_avg is not None and stage_avg < 0:
        risk_discount -= 0.15
        notes.append(f'当前市场阶段历史 1D 均值偏弱 ({stage_avg}%)，自动降档风险预算。')
    if stage_win_rate is not None and stage_win_rate < 45:
        risk_discount -= 0.1
        notes.append(f'当前市场阶段历史胜率偏低 ({stage_win_rate}%)，进一步收缩仓位。')
    if recent_negative_streak >= 2:
        risk_discount -= min(0.25, recent_negative_streak * 0.05)
        notes.append(f'近期连续失利 {recent_negative_streak} 笔，触发连亏降档。')
    if cooldown:
        risk_discount = min(risk_discount, 0.55)
        notes.append('触发冷静模式：仅允许最强候选进入计划。')

    risk_discount = max(0.35, round(risk_discount, 2))

    candidate_diagnostics: list[dict[str, Any]] = []
    theme_count: dict[str, int] = defaultdict(int)
    for item in candidate_plan:
        symbol = item['symbol']
        theme = str(item.get('theme') or '未分类')
        theme_count[theme] += 1
        item_trades = [t for t in historical_trades if t.get('symbol') == symbol and t.get('return_1d') is not None]
        strategy_scores = []
        governor_map = {entry['strategy']: entry for entry in (strategy_governor.get('items') or [])}
        frozen_hit = False
        strategy_weight_multiplier = 1.0
        for strategy in item.get('strategies') or []:
            avg = _bucket_avg_return(historical_trades, 'strategy', strategy)
            if avg is not None:
                strategy_scores.append(avg)
            governor_item = governor_map.get(strategy)
            if governor_item:
                strategy_weight_multiplier *= float(governor_item.get('weight_multiplier') or 1.0)
                if governor_item.get('status') == 'frozen':
                    frozen_hit = True
        avg_strategy_edge = round(mean(strategy_scores), 2) if strategy_scores else None
        symbol_avg_1d = round(mean(float(t['return_1d']) for t in item_trades), 2) if item_trades else None
        symbol_win_rate = round(sum(1 for t in item_trades if float(t['return_1d']) > 0) / len(item_trades) * 100, 2) if item_trades else None
        quality_multiplier = 1.0
        if item.get('resonance_level') == 'A':
            quality_multiplier += 0.18
        elif item.get('resonance_level') == 'B':
            quality_multiplier += 0.08
        elif item.get('resonance_level') == 'C':
            quality_multiplier -= 0.12
        if len(item.get('strategies') or []) >= 2:
            quality_multiplier += 0.08
        if avg_strategy_edge is not None:
            quality_multiplier += max(-0.12, min(0.2, avg_strategy_edge / 10))
        if symbol_avg_1d is not None:
            quality_multiplier += max(-0.12, min(0.18, symbol_avg_1d / 12))
        quality_multiplier *= strategy_weight_multiplier
        if frozen_hit:
            quality_multiplier = min(quality_multiplier, 0.35)

        candidate_diagnostics.append({
            'symbol': symbol,
            'theme': theme,
            'avg_strategy_edge_1d': avg_strategy_edge,
            'symbol_avg_return_1d': symbol_avg_1d,
            'symbol_win_rate_1d_pct': symbol_win_rate,
            'strategy_weight_multiplier': round(strategy_weight_multiplier, 2),
            'blocked_by_governor': frozen_hit,
            'quality_multiplier': round(max(0.25, min(1.65, quality_multiplier)), 2),
        })

    crowded_themes = [theme for theme, count in theme_count.items() if count >= 2]
    if crowded_themes:
        notes.append(f'候选题材出现拥挤：{", ".join(crowded_themes[:3])}，后续按题材上限裁剪。')

    if strategy_governor.get('notes'):
        notes.extend(strategy_governor['notes'])

    return {
        'risk_mode': risk_mode,
        'market_stage': market_stage,
        'limits': limits,
        'risk_discount': risk_discount,
        'cooldown': cooldown,
        'recent_negative_streak': recent_negative_streak,
        'historical_stage_avg_return_1d': stage_avg,
        'historical_stage_win_rate_1d_pct': stage_win_rate,
        'strategy_governor': strategy_governor,
        'candidate_diagnostics': candidate_diagnostics,
        'notes': notes,
    }
