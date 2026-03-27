from __future__ import annotations

from typing import Any

from packages.python.experiment_lab import run_experiment_lab


def get_adaptive_parameter_profile(limit: int = 160) -> dict[str, Any]:
    experiment = run_experiment_lab(limit=limit)
    best = experiment.get('best') or {}
    if not best:
        return {
            'active_profile': 'fallback',
            'params': {},
            'notes': ['暂无实验结果，使用默认参数。'],
            'source': 'experiment_lab',
        }

    return {
        'active_profile': best.get('name', 'unknown'),
        'params': {
            'stop_loss_pct': best.get('stop_loss_pct'),
            'take_profit_pct': best.get('take_profit_pct'),
            'partial_take_profit_pct': best.get('partial_take_profit_pct'),
            'trail_protect_pct': best.get('trail_protect_pct'),
            'signal_weight_leader': best.get('signal_weight_leader'),
            'signal_weight_hotmoney': best.get('signal_weight_hotmoney'),
        },
        'notes': [
            f"当前实验层推荐参数集：{best.get('name')}",
            f"avg_score={best.get('avg_score')}, win_rate={best.get('win_rate_pct')}%",
        ],
        'source': 'experiment_lab',
        'ranking': experiment.get('ranked') or [],
    }
