from __future__ import annotations

import json
from typing import Any

from packages.python.exit_engine import evaluate_exit_decision
from packages.python.storage import get_conn, init_db, save_paper_trade_attribution


def _find_candidate_price(symbol: str, stocks: list[dict[str, Any]]) -> float:
    for stock in stocks:
        if stock.get('symbol') == symbol:
            return float(stock.get('close') or 0)
    return 0.0


def run_paper_execution(payload: dict[str, Any], stocks: list[dict[str, Any]]) -> dict[str, Any]:
    init_db()
    trade_date = payload['trade_date']
    plan = payload.get('portfolio_plan') or {}
    risk_mode = str(plan.get('risk_mode') or 'defensive_probe')
    execution_policy = str(plan.get('execution_policy') or 'paper_only')
    market_stage = str(payload.get('market', {}).get('market_sentiment_stage') or 'ice')
    opened: list[dict[str, Any]] = []
    closed: list[dict[str, Any]] = []
    rebalanced: list[dict[str, Any]] = []

    if execution_policy not in {'paper_only', 'semi_auto'}:
        return {
            'opened': [],
            'closed': [],
            'rebalanced': [],
            'opened_count': 0,
            'closed_count': 0,
            'rebalanced_count': 0,
            'execution_skipped': True,
            'execution_policy': execution_policy,
        }

    with get_conn() as conn:
        open_positions = conn.execute(
            "SELECT * FROM paper_positions WHERE status = 'open' ORDER BY id ASC"
        ).fetchall()
        planned_by_symbol = {item['symbol']: item for item in (plan.get('candidate_plan') or [])}

        for row in open_positions:
            position = dict(row)
            current_price = _find_candidate_price(position['symbol'], stocks)
            if current_price <= 0:
                continue
            planned = planned_by_symbol.get(position['symbol'])
            decision = evaluate_exit_decision(
                trade_date=trade_date,
                risk_mode=risk_mode,
                current_price=current_price,
                position=position,
                planned=planned,
            )
            ret_pct = float(decision['return_pct'])
            peak_return_pct = float(decision.get('peak_return_pct') or ret_pct)
            conn.execute(
                "UPDATE paper_positions SET peak_return_pct = ?, lifecycle_state = ? WHERE id = ?",
                (peak_return_pct, decision.get('next_state', 'open') if decision.get('action') == 'partial_take_profit' else position.get('lifecycle_state', 'open'), position['id']),
            )
            if decision.get('action') == 'partial_take_profit':
                current_weight = float(position['target_weight_pct'])
                reduced_weight = round(max(3.0, current_weight * 0.5), 1)
                conn.execute(
                    "UPDATE paper_positions SET target_weight_pct = ?, partial_exit_taken = 1, lifecycle_state = 'scaled_out', plan_json = ? WHERE id = ?",
                    (reduced_weight, json.dumps(planned or {}, ensure_ascii=False), position['id']),
                )
                conn.execute(
                    "INSERT INTO paper_trades (trade_date, symbol, name, side, price, weight_pct, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (trade_date, position['symbol'], position['name'], 'sell', current_price, round(current_weight - reduced_weight, 1), 'paper_partial_take_profit'),
                )
                rebalanced.append({
                    'symbol': position['symbol'],
                    'name': position['name'],
                    'from_weight_pct': current_weight,
                    'to_weight_pct': reduced_weight,
                    'reason': 'partial_take_profit',
                })
                save_paper_trade_attribution({
                    'trade_date': trade_date,
                    'symbol': position['symbol'],
                    'name': position['name'],
                    'action': 'partial_take_profit',
                    'lifecycle_state': 'scaled_out',
                    'reason': 'partial_take_profit',
                    'return_pct': ret_pct,
                    'peak_return_pct': peak_return_pct,
                    'weight_before_pct': current_weight,
                    'weight_after_pct': reduced_weight,
                    'meta': {
                        'risk_mode': risk_mode,
                        'thresholds': decision.get('thresholds') or {},
                    },
                }, conn=conn)
                continue
            if decision['should_close']:
                reason = str(decision['reason'])
                if reason == 'plan_removed':
                    exit_note = 'paper_rebalance_exit'
                elif reason == 'resonance_drop':
                    exit_note = 'paper_resonance_exit'
                elif reason == 'role_break':
                    exit_note = 'paper_riskmode_exit'
                elif reason == 'time_exit':
                    exit_note = 'paper_time_exit'
                elif reason == 'stop_loss':
                    exit_note = 'paper_stop_loss'
                elif reason == 'take_profit':
                    exit_note = 'paper_take_profit'
                elif reason == 'trailing_stop':
                    exit_note = 'paper_trailing_stop_exit'
                elif reason == 'break_even_exit':
                    exit_note = 'paper_break_even_exit'
                elif reason == 'rebalance_down':
                    exit_note = 'paper_rebalance_down_exit'
                else:
                    exit_note = 'paper_exit'
                conn.execute(
                    """
                    UPDATE paper_positions
                    SET status = 'closed', closed_trade_date = ?, exit_price = ?, realized_return_pct = ?
                    WHERE id = ?
                    """,
                    (trade_date, current_price, ret_pct, position['id']),
                )
                conn.execute(
                    "INSERT INTO paper_trades (trade_date, symbol, name, side, price, weight_pct, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (trade_date, position['symbol'], position['name'], 'sell', current_price, position['target_weight_pct'], exit_note),
                )
                closed.append({
                    'symbol': position['symbol'],
                    'name': position['name'],
                    'exit_price': current_price,
                    'realized_return_pct': ret_pct,
                    'exit_reason': exit_note,
                })
                save_paper_trade_attribution({
                    'trade_date': trade_date,
                    'symbol': position['symbol'],
                    'name': position['name'],
                    'action': 'full_exit',
                    'lifecycle_state': 'closed',
                    'reason': reason,
                    'return_pct': ret_pct,
                    'peak_return_pct': peak_return_pct,
                    'weight_before_pct': float(position['target_weight_pct']),
                    'weight_after_pct': 0.0,
                    'meta': {
                        'risk_mode': risk_mode,
                        'exit_note': exit_note,
                        'thresholds': decision.get('thresholds') or {},
                    },
                }, conn=conn)
                continue

            planned = planned_by_symbol.get(position['symbol'])
            if planned:
                current_weight = float(position['target_weight_pct'])
                target_weight = float(planned.get('target_weight_pct') or current_weight)
                if abs(target_weight - current_weight) >= 4:
                    conn.execute(
                        "UPDATE paper_positions SET target_weight_pct = ?, plan_json = ? WHERE id = ?",
                        (target_weight, json.dumps(planned, ensure_ascii=False), position['id']),
                    )
                    conn.execute(
                        "INSERT INTO paper_trades (trade_date, symbol, name, side, price, weight_pct, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (trade_date, position['symbol'], position['name'], 'rebalance', current_price, target_weight, 'paper_rebalance_adjust'),
                    )
                    rebalanced.append({
                        'symbol': position['symbol'],
                        'name': position['name'],
                        'from_weight_pct': current_weight,
                        'to_weight_pct': target_weight,
                    })

        existing_open = {
            row['symbol'] for row in conn.execute("SELECT symbol FROM paper_positions WHERE status = 'open'").fetchall()
        }
        for item in plan.get('candidate_plan') or []:
            if item['symbol'] in existing_open:
                continue
            if float(item.get('target_weight_pct') or 0) < 3:
                continue
            entry_price = _find_candidate_price(item['symbol'], stocks)
            if entry_price <= 0:
                continue
            conn.execute(
                """
                INSERT INTO paper_positions (
                    symbol, name, opened_trade_date, entry_price, target_weight_pct, status, theme, strategy_json, plan_json
                ) VALUES (?, ?, ?, ?, ?, 'open', ?, ?, ?)
                """,
                (
                    item['symbol'],
                    item['name'],
                    trade_date,
                    entry_price,
                    item['target_weight_pct'],
                    item.get('theme', ''),
                    json.dumps(item.get('strategies', []), ensure_ascii=False),
                    json.dumps(item, ensure_ascii=False),
                ),
            )
            conn.execute(
                "INSERT INTO paper_trades (trade_date, symbol, name, side, price, weight_pct, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (trade_date, item['symbol'], item['name'], 'buy', entry_price, item['target_weight_pct'], 'paper_entry'),
            )
            opened.append({
                'symbol': item['symbol'],
                'name': item['name'],
                'entry_price': entry_price,
                'target_weight_pct': item['target_weight_pct'],
            })

    return {
        'opened': opened,
        'closed': closed,
        'rebalanced': rebalanced,
        'opened_count': len(opened),
        'closed_count': len(closed),
        'rebalanced_count': len(rebalanced),
        'execution_skipped': False,
        'execution_policy': execution_policy,
        'risk_mode': risk_mode,
        'market_stage': market_stage,
    }


def list_paper_positions() -> list[dict[str, Any]]:
    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM paper_positions ORDER BY status DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def list_paper_trades(limit: int = 100) -> list[dict[str, Any]]:
    init_db()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM paper_trades ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def paper_portfolio_summary(stocks: list[dict[str, Any]]) -> dict[str, Any]:
    positions = list_paper_positions()
    trades = list_paper_trades(limit=500)

    open_positions = [p for p in positions if p['status'] == 'open']
    closed_positions = [p for p in positions if p['status'] == 'closed']

    unrealized = 0.0
    open_weight = 0.0
    for position in open_positions:
        current_price = _find_candidate_price(position['symbol'], stocks)
        if current_price <= 0:
            continue
        entry_price = float(position['entry_price'])
        ret_pct = (current_price / entry_price - 1) * 100
        unrealized += ret_pct * float(position['target_weight_pct']) / 100
        open_weight += float(position['target_weight_pct'])

    realized = sum(float(p.get('realized_return_pct') or 0) * float(p.get('target_weight_pct') or 0) / 100 for p in closed_positions)
    wins = sum(1 for p in closed_positions if float(p.get('realized_return_pct') or 0) > 0)

    return {
        'open_positions': len(open_positions),
        'closed_positions': len(closed_positions),
        'open_weight_pct': round(open_weight, 2),
        'unrealized_pnl_pct': round(unrealized, 2),
        'realized_pnl_pct': round(realized, 2),
        'total_pnl_pct': round(unrealized + realized, 2),
        'win_rate_pct': round(wins / max(len(closed_positions), 1) * 100, 2) if closed_positions else 0.0,
        'trade_count': len(trades),
    }
