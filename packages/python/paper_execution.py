from __future__ import annotations

import json
from typing import Any

from packages.python.storage import get_conn, init_db


MAX_HOLD_DAYS = 5
STOP_LOSS_PCT = -5.0
TAKE_PROFIT_PCT = 12.0


def _find_candidate_price(symbol: str, stocks: list[dict[str, Any]]) -> float:
    for stock in stocks:
        if stock.get('symbol') == symbol:
            return float(stock.get('close') or 0)
    return 0.0


def run_paper_execution(payload: dict[str, Any], stocks: list[dict[str, Any]]) -> dict[str, Any]:
    init_db()
    trade_date = payload['trade_date']
    plan = payload.get('portfolio_plan') or {}
    opened: list[dict[str, Any]] = []
    closed: list[dict[str, Any]] = []

    with get_conn() as conn:
        open_positions = conn.execute(
            "SELECT * FROM paper_positions WHERE status = 'open' ORDER BY id ASC"
        ).fetchall()

        for row in open_positions:
            position = dict(row)
            current_price = _find_candidate_price(position['symbol'], stocks)
            if current_price <= 0:
                continue
            entry_price = float(position['entry_price'])
            ret_pct = round((current_price / entry_price - 1) * 100, 2)
            hold_days = max(0, int(trade_date.replace('-', '')) - int(position['opened_trade_date'].replace('-', '')))
            should_close = ret_pct <= STOP_LOSS_PCT or ret_pct >= TAKE_PROFIT_PCT or hold_days >= MAX_HOLD_DAYS
            if should_close:
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
                    (trade_date, position['symbol'], position['name'], 'sell', current_price, position['target_weight_pct'], 'paper_exit'),
                )
                closed.append({
                    'symbol': position['symbol'],
                    'name': position['name'],
                    'exit_price': current_price,
                    'realized_return_pct': ret_pct,
                })

        existing_open = {
            row['symbol'] for row in conn.execute("SELECT symbol FROM paper_positions WHERE status = 'open'").fetchall()
        }
        for item in plan.get('candidate_plan') or []:
            if item['symbol'] in existing_open:
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
        'opened_count': len(opened),
        'closed_count': len(closed),
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
