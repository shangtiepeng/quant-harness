from __future__ import annotations

from statistics import mean
from typing import Any

from packages.python.backtest import backtest_signals


FREEZE_THRESHOLD = -1.5
BOOST_THRESHOLD = 1.5


def build_strategy_governor(history_limit: int = 200) -> dict[str, Any]:
    backtest = backtest_signals(limit=history_limit, kline_days=60)
    trades = backtest.get('trades') or []

    strategies = sorted({str(t.get('strategy') or '') for t in trades if t.get('strategy')})
    items: list[dict[str, Any]] = []
    enabled: list[str] = []
    frozen: list[str] = []

    for strategy in strategies:
        subset = [t for t in trades if str(t.get('strategy') or '') == strategy and t.get('return_1d') is not None]
        if not subset:
            continue
        returns_1d = [float(t['return_1d']) for t in subset if t.get('return_1d') is not None]
        returns_3d = [float(t['return_3d']) for t in subset if t.get('return_3d') is not None]
        drawdowns = [float(t['max_drawdown_5d']) for t in subset if t.get('max_drawdown_5d') is not None]
        avg_1d = round(mean(returns_1d), 2) if returns_1d else None
        avg_3d = round(mean(returns_3d), 2) if returns_3d else None
        avg_dd = round(mean(drawdowns), 2) if drawdowns else None
        win_rate = round(sum(1 for x in returns_1d if x > 0) / len(returns_1d) * 100, 2) if returns_1d else None

        score = 0.0
        if avg_1d is not None:
            score += avg_1d * 12
        if avg_3d is not None:
            score += avg_3d * 6
        if avg_dd is not None:
            score += avg_dd * 3
        if win_rate is not None:
            score += (win_rate - 50) * 0.6
        score = round(score, 2)

        if avg_1d is not None and avg_1d <= FREEZE_THRESHOLD:
            status = 'frozen'
            weight_multiplier = 0.0
            frozen.append(strategy)
        elif avg_1d is not None and avg_1d >= BOOST_THRESHOLD:
            status = 'boosted'
            weight_multiplier = 1.25
            enabled.append(strategy)
        else:
            status = 'normal'
            weight_multiplier = 1.0
            enabled.append(strategy)

        items.append({
            'strategy': strategy,
            'count': len(subset),
            'avg_return_1d': avg_1d,
            'avg_return_3d': avg_3d,
            'avg_max_drawdown_5d': avg_dd,
            'win_rate_1d_pct': win_rate,
            'score': score,
            'status': status,
            'weight_multiplier': weight_multiplier,
        })

    items = sorted(items, key=lambda x: (x['status'] == 'boosted', x['score']), reverse=True)
    notes: list[str] = []
    if frozen:
        notes.append(f"近期表现失效，冻结策略：{', '.join(frozen)}")
    boosted = [item['strategy'] for item in items if item['status'] == 'boosted']
    if boosted:
        notes.append(f"近期表现较强，提升权重：{', '.join(boosted)}")

    return {
        'history_signal_count': backtest.get('history_signal_count', 0),
        'trade_count': backtest.get('trade_count', 0),
        'enabled_strategies': enabled,
        'frozen_strategies': frozen,
        'items': items,
        'notes': notes,
    }
