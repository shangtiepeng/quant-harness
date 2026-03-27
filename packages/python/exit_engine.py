from __future__ import annotations

from typing import Any

from packages.python.adaptive_params import get_adaptive_parameter_profile


DEFAULT_STOP_LOSS_PCT = -5.0
DEFAULT_TAKE_PROFIT_PCT = 12.0
DEFAULT_PARTIAL_TAKE_PROFIT_PCT = 6.0
DEFAULT_BREAK_EVEN_TRIGGER_PCT = 3.0
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

    adaptive_profile = get_adaptive_parameter_profile(limit=160)
    adaptive_params = adaptive_profile.get('params') or {}

    ret_pct = round((current_price / entry_price - 1) * 100, 2)
    hold_days = _rough_hold_days(str(position.get('opened_trade_date') or trade_date), trade_date)
    hold_limit = int(RISK_MODE_HOLD_LIMIT.get(risk_mode, 5))
    stop_loss_pct = float(adaptive_params.get('stop_loss_pct') or RISK_MODE_STOP.get(risk_mode, DEFAULT_STOP_LOSS_PCT))
    take_profit_pct = float(adaptive_params.get('take_profit_pct') or RISK_MODE_TP.get(risk_mode, DEFAULT_TAKE_PROFIT_PCT))

    target_weight = float(position.get('target_weight_pct') or 0)
    planned_weight = float((planned or {}).get('target_weight_pct') or 0)
    removed_from_plan = planned is None
    resonance_level = str((planned or {}).get('resonance_level') or '')
    role = str((planned or {}).get('role') or (planned or {}).get('resonance_role') or '')
    partial_exit_taken = bool(int(position.get('partial_exit_taken') or 0))
    peak_return_pct = max(float(position.get('peak_return_pct') or 0), ret_pct)
    lifecycle_state = str(position.get('lifecycle_state') or 'open')

    resonance_drop = resonance_level in {'C', 'D'}
    role_break = role in {'noise', 'follower'} and risk_mode in {'defensive_probe', 'risk_control'}
    time_exit = hold_days >= hold_limit
    stop_loss = ret_pct <= stop_loss_pct
    take_profit = ret_pct >= take_profit_pct
    rebalance_down = planned is not None and planned_weight > 0 and planned_weight < target_weight - 3.5
    partial_take_profit_pct = float(adaptive_params.get('partial_take_profit_pct') or DEFAULT_PARTIAL_TAKE_PROFIT_PCT)
    trail_protect_pct = float(adaptive_params.get('trail_protect_pct') or DEFAULT_TRAIL_PROTECT_PCT)
    partial_take_profit = (not partial_exit_taken) and ret_pct >= partial_take_profit_pct
    break_even_exit = partial_exit_taken and ret_pct <= 0 and peak_return_pct >= DEFAULT_BREAK_EVEN_TRIGGER_PCT
    trailing_stop = peak_return_pct >= partial_take_profit_pct and (peak_return_pct - ret_pct) >= trail_protect_pct

    should_close = any([
        removed_from_plan,
        resonance_drop,
        role_break,
        time_exit and not partial_take_profit,
        stop_loss,
        take_profit,
        rebalance_down,
        break_even_exit,
        trailing_stop,
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
    elif trailing_stop:
        reason = 'trailing_stop'
    elif break_even_exit:
        reason = 'break_even_exit'
    elif time_exit:
        reason = 'time_exit'
    elif rebalance_down:
        reason = 'rebalance_down'
    else:
        reason = 'hold'

    action = 'hold'
    if partial_take_profit and not should_close:
        action = 'partial_take_profit'
    elif should_close:
        action = 'full_exit'

    next_state = lifecycle_state
    if action == 'partial_take_profit':
        next_state = 'scaled_out'
    elif should_close:
        next_state = 'closed'

    return {
        'should_close': should_close,
        'reason': reason,
        'action': action,
        'hold_days': hold_days,
        'return_pct': ret_pct,
        'peak_return_pct': peak_return_pct,
        'partial_take_profit': partial_take_profit,
        'partial_exit_taken': partial_exit_taken,
        'next_state': next_state,
        'thresholds': {
            'hold_limit': hold_limit,
            'stop_loss_pct': stop_loss_pct,
            'take_profit_pct': take_profit_pct,
            'partial_take_profit_pct': partial_take_profit_pct,
            'break_even_trigger_pct': DEFAULT_BREAK_EVEN_TRIGGER_PCT,
            'trail_protect_pct': trail_protect_pct,
            'adaptive_profile': adaptive_profile.get('active_profile'),
        },
    }
