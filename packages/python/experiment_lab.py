from __future__ import annotations

from statistics import mean
from typing import Any

from packages.python.backtest import backtest_signals


EXPERIMENTS: list[dict[str, Any]] = [
    {
        'name': 'baseline',
        'stop_loss_pct': -4.0,
        'take_profit_pct': 8.0,
        'partial_take_profit_pct': 6.0,
        'trail_protect_pct': 4.0,
        'signal_weight_leader': 1.25,
        'signal_weight_hotmoney': 1.0,
    },
    {
        'name': 'tight_risk',
        'stop_loss_pct': -3.0,
        'take_profit_pct': 7.0,
        'partial_take_profit_pct': 5.0,
        'trail_protect_pct': 3.0,
        'signal_weight_leader': 1.15,
        'signal_weight_hotmoney': 0.9,
    },
    {
        'name': 'let_winners_run',
        'stop_loss_pct': -5.0,
        'take_profit_pct': 12.0,
        'partial_take_profit_pct': 7.0,
        'trail_protect_pct': 5.0,
        'signal_weight_leader': 1.35,
        'signal_weight_hotmoney': 1.0,
    },
    {
        'name': 'balanced_rotation',
        'stop_loss_pct': -4.5,
        'take_profit_pct': 10.0,
        'partial_take_profit_pct': 6.0,
        'trail_protect_pct': 4.0,
        'signal_weight_leader': 1.1,
        'signal_weight_hotmoney': 1.1,
    },
]


def _score_trade(trade: dict[str, Any], exp: dict[str, Any]) -> float | None:
    r1 = trade.get('return_1d')
    r3 = trade.get('return_3d')
    drawdown = trade.get('max_drawdown_5d')
    if r1 is None:
        return None

    strategy = str(trade.get('strategy') or '')
    strategy_weight = 1.0
    if strategy == 'leader':
        strategy_weight = float(exp['signal_weight_leader'])
    elif strategy == 'hotmoney':
        strategy_weight = float(exp['signal_weight_hotmoney'])

    realized = float(r1)
    if realized <= float(exp['stop_loss_pct']):
        realized = float(exp['stop_loss_pct'])
    elif r3 is not None and float(r3) >= float(exp['take_profit_pct']):
        realized = float(exp['take_profit_pct'])
    elif r3 is not None and float(r3) >= float(exp['partial_take_profit_pct']):
        realized = (float(exp['partial_take_profit_pct']) * 0.5) + (float(r3) * 0.5)

    if drawdown is not None and abs(float(drawdown)) >= float(exp['trail_protect_pct']) + 2:
        realized -= 0.8

    return round(realized * strategy_weight, 3)


def run_experiment_lab(limit: int = 160) -> dict[str, Any]:
    backtest = backtest_signals(limit=limit, kline_days=60)
    trades = backtest.get('trades') or []
    results: list[dict[str, Any]] = []

    for exp in EXPERIMENTS:
        scores = [score for trade in trades if (score := _score_trade(trade, exp)) is not None]
        if not scores:
            results.append({
                **exp,
                'trade_count': 0,
                'avg_score': None,
                'win_rate_pct': None,
                'total_score': None,
            })
            continue
        result = {
            **exp,
            'trade_count': len(scores),
            'avg_score': round(mean(scores), 3),
            'win_rate_pct': round(sum(1 for x in scores if x > 0) / len(scores) * 100, 2),
            'total_score': round(sum(scores), 3),
        }
        results.append(result)

    ranked = sorted(results, key=lambda x: ((x.get('avg_score') if x.get('avg_score') is not None else -999), x.get('win_rate_pct') or 0), reverse=True)
    best = ranked[0] if ranked else None
    return {
        'history_signal_count': backtest.get('history_signal_count', 0),
        'trade_count': backtest.get('trade_count', 0),
        'best': best,
        'ranked': ranked,
        'notes': [
            '这是轻量实验层，不是严格成交级回测引擎。',
            '用于快速比较规则方向，后续可升级为完整参数搜索。',
        ],
    }
