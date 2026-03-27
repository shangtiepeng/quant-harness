from __future__ import annotations

from typing import Any


DEFAULT_STOP_LOSS_PCT = -5.0
DEFAULT_TAKE_PROFIT_PCT = 12.0
DEFAULT_TRAIL_PROTECT_PCT = 4.0
RISK_MODE_HOLD_LIMIT = {
    'defensive_probe': 3,
    'risk_control': 4,
    'selective_attack': 5,
    'active_attack': 5,
}
RISK_MODE_STOP = {
    'defensive_probe': -4.0,
    'risk_control': -4.5,
    'selective_attack': -5.5,
    'active_attack': -6.5,
}
RISK_MODE_TP = {
    'defensive_probe': 8.0,
    'risk_control': 10.0,
    'selective_attack': 12.0,
    'active_attack': 15.0,
}


def _rough_hold_days(opened_trade_date: str, trade_date: str) -> int:
    try:
        return max(0, int(trade_date.replace('-', '')) - int(opened_trade_date.replace('-', '')))
    except Exception:
        return 0


def evaluate_exit_decision(
    *,
    trade_date: str,
    risk_mode: str,
    current_price: float,
    position: dict[str, Any],
    planned: dict[str, Any] | None,
) -> dict[str, Any]:
    entry_price = float(position.get('entry_price') or 0)
    if entry_price <= 0 or current_price <= 0:
        return {
            'should_close': False,
            'reason': 'invalid_price',
            'hold_days': 0,
            'return_pct': 0.0,
            'thresholds': {},
        }

    ret_pct = round((current_price / entry_price - 1) * 100, 2)
    hold_days = _rough_hold_days(str(position.get('opened_trade_date') or trade_date), trade_date)
    hold_limit = int(RISK_MODE_HOLD_LIMIT.get(risk_mode, 5))
    stop_loss_pct = float(RISK_MODE_STOP.get(risk_mode, DEFAULT_STOP_LOSS_PCT))
    take_profit_pct = float(RISK_MODE_TP.get(risk_mode, DEFAULT_TAKE_PROFIT_PCT))

    target_weight = float(position.get('target_weight_pct') or 0)
    planned_weight = float((planned or {}).get('target_weight_pct') or 0)
    removed_from_plan = planned is None
    resonance_level = str((planned or {}).get('resonance_level') or '')
    role = str((planned or {}).get('role') or (planned or {}).get('resonance_role') or '')
    resonance_drop = resonance_level in {'C', 'D'}
    role_break = role in {'noise', 'follower'} and risk_mode in {'defensive_probe', 'risk_control'}
    time_exit = hold_days >= hold_limit
    stop_loss = ret_pct <= stop_loss_pct
    take_profit = ret_pct >= take_profit_pct
    rebalance_down = planned is not None and planned_weight > 0 and planned_weight < target_weight - 3.5

    should_close = any([
        removed_from_plan,
        resonance_drop,
        role_break,
        time_exit,
        stop_loss,
        take_profit,
        rebalance_down,
    ])

    if removed_from_plan:
        reason = 'plan_removed'
    elif resonance_drop:
        reason = 'resonance_drop'
    elif role_break:
        reason = 'role_break'
    elif stop_loss:
        reason = 'stop_loss'
    elif take_profit:
        reason = 'take_profit'
    elif time_exit:
        reason = 'time_exit'
    elif rebalance_down:
        reason = 'rebalance_down'
    else:
        reason = 'hold'

    return {
        'should_close': should_close,
        'reason': reason,
        'hold_days': hold_days,
        'return_pct': ret_pct,
        'thresholds': {
            'hold_limit': hold_limit,
            'stop_loss_pct': stop_loss_pct,
            'take_profit_pct': take_profit_pct,
            'trail_protect_pct': DEFAULT_TRAIL_PROTECT_PCT,
        },
    }
