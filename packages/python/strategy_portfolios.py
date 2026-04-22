from __future__ import annotations

import json
from typing import Any

from packages.python.exit_engine import evaluate_exit_decision
from packages.python.storage import get_conn, init_db


INITIAL_CAPITAL = 1_000_000.0
PORTFOLIOS: list[dict[str, Any]] = [
    {
        'key': 'mainline_leader',
        'name': '主线龙头组合',
        'description': '只做主线龙头与前排核心，频率低，强调确定性。',
        'styles': {'roles': ['mainline_leader', 'frontline_core'], 'levels': ['A', 'B'], 'min_strategy_count': 1, 'max_positions': 3, 'cash_buffer_pct': 28},
    },
    {
        'key': 'double_resonance',
        'name': '双确认高共振组合',
        'description': '至少双策略共识，优先 A/B 级共振，偏胜率优先。',
        'styles': {'roles': ['mainline_leader', 'frontline_core', 'secondary_rotation'], 'levels': ['A', 'B'], 'min_strategy_count': 2, 'max_positions': 4, 'cash_buffer_pct': 20},
    },
    {
        'key': 'defensive_rotation',
        'name': '防守轮动组合',
        'description': '偏防守，控制回撤，只做高质量轮动与低风险暴露。',
        'styles': {'roles': ['frontline_core', 'secondary_rotation', 'follower'], 'levels': ['A', 'B', 'C'], 'min_strategy_count': 1, 'max_positions': 5, 'cash_buffer_pct': 35},
    },
]


def ensure_strategy_portfolio_tables() -> None:
    init_db()
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS strategy_portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_key TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                initial_capital REAL NOT NULL,
                cash REAL NOT NULL,
                nav REAL NOT NULL,
                config_json TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS strategy_portfolio_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_key TEXT NOT NULL,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                opened_trade_date TEXT NOT NULL,
                entry_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                cost_basis REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                theme TEXT,
                signal_json TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                closed_trade_date TEXT,
                exit_price REAL,
                realized_pnl REAL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS strategy_portfolio_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_key TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                name TEXT NOT NULL,
                side TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                amount REAL NOT NULL,
                note TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS strategy_portfolio_nav_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_key TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                nav REAL NOT NULL,
                cash REAL NOT NULL,
                market_value REAL NOT NULL,
                note TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def bootstrap_strategy_portfolios() -> None:
    ensure_strategy_portfolio_tables()
    with get_conn() as conn:
        existing = {row['portfolio_key'] for row in conn.execute('SELECT portfolio_key FROM strategy_portfolios').fetchall()}
        for item in PORTFOLIOS:
            if item['key'] in existing:
                continue
            conn.execute(
                """
                INSERT INTO strategy_portfolios (portfolio_key, name, initial_capital, cash, nav, config_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    item['key'],
                    item['name'],
                    INITIAL_CAPITAL,
                    INITIAL_CAPITAL,
                    INITIAL_CAPITAL,
                    json.dumps(item, ensure_ascii=False),
                ),
            )


def _load_config_map() -> dict[str, dict[str, Any]]:
    return {item['key']: item for item in PORTFOLIOS}


def _candidate_matches(candidate: dict[str, Any], styles: dict[str, Any]) -> bool:
    role = str(candidate.get('resonance_role') or 'noise')
    level = str(candidate.get('resonance_level') or 'D')
    strategy_count = int(candidate.get('strategy_count') or len(candidate.get('strategies') or []))
    risk_level = str(candidate.get('risk_level') or 'high')
    if role not in set(styles.get('roles') or []):
        return False
    if level not in set(styles.get('levels') or []):
        return False
    if strategy_count < int(styles.get('min_strategy_count') or 1):
        return False
    if styles.get('cash_buffer_pct', 0) >= 30 and risk_level == 'high':
        return False
    return True


def _target_candidates_for_portfolio(candidates: list[dict[str, Any]], portfolio_key: str) -> list[dict[str, Any]]:
    config = _load_config_map()[portfolio_key]
    styles = config['styles']
    selected = [item for item in candidates if _candidate_matches(item, styles)]
    return selected[: int(styles.get('max_positions') or 3)]


def _current_prices(stocks: list[dict[str, Any]]) -> dict[str, float]:
    return {item['symbol']: float(item.get('close') or 0) for item in stocks if item.get('symbol')}


def _build_market_stocks(payload: dict[str, Any]) -> list[dict[str, Any]]:
    market = payload.get('market') or {}
    by_symbol: dict[str, dict[str, Any]] = {}

    for key in ('top_gainers', 'top_losers'):
        for item in market.get(key) or []:
            symbol = item.get('symbol')
            if not symbol:
                continue
            by_symbol[symbol] = {
                'symbol': symbol,
                'close': float(item.get('close') or 0),
            }

    for item in payload.get('candidates') or []:
        symbol = item.get('symbol')
        if not symbol or symbol in by_symbol:
            continue
        by_symbol[symbol] = {
            'symbol': symbol,
            'close': float(item.get('close') or 0),
        }

    for item in payload.get('signals') or []:
        symbol = item.get('symbol')
        if not symbol or symbol in by_symbol:
            continue
        by_symbol[symbol] = {
            'symbol': symbol,
            'close': float(item.get('close') or 0),
        }

    return list(by_symbol.values())


def run_strategy_portfolios(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    bootstrap_strategy_portfolios()
    payload = payload or {'trade_date': '', 'candidates': [], 'signals': [], 'market': {}}
    trade_date = payload.get('trade_date') or ''
    candidates = payload.get('candidates') or []
    market_stocks = _build_market_stocks(payload)
    price_map = _current_prices(market_stocks)

    with get_conn() as conn:
        portfolios = [dict(row) for row in conn.execute('SELECT * FROM strategy_portfolios ORDER BY id ASC').fetchall()]
        for portfolio in portfolios:
            key = portfolio['portfolio_key']
            config = json.loads(portfolio['config_json'])
            styles = config['styles']
            open_rows = [dict(row) for row in conn.execute(
                "SELECT * FROM strategy_portfolio_positions WHERE portfolio_key = ? AND status = 'open' ORDER BY id ASC",
                (key,),
            ).fetchall()]
            targets = _target_candidates_for_portfolio(candidates, key)
            target_symbols = {item['symbol'] for item in targets}

            cash = float(portfolio['cash'])
            initial_capital = float(portfolio['initial_capital'])
            max_positions = max(int(styles.get('max_positions') or 3), 1)
            allocatable = initial_capital * (1 - float(styles.get('cash_buffer_pct') or 0) / 100)
            per_position_budget = allocatable / max_positions

            target_map = {item['symbol']: item for item in targets}
            for row in open_rows:
                current_price = price_map.get(row['symbol']) or row['entry_price']
                signal_data = json.loads(row['signal_json'])
                enriched_position = {
                    **row,
                    'entry_price': row['entry_price'],
                    'target_weight_pct': round(float(row['cost_basis']) / max(initial_capital, 1) * 100, 2),
                    'opened_trade_date': row['opened_trade_date'],
                }
                planned = target_map.get(row['symbol'])
                decision = evaluate_exit_decision(
                    trade_date=trade_date,
                    risk_mode='selective_attack',
                    current_price=current_price,
                    position=enriched_position,
                    planned=planned or signal_data,
                )
                should_close = bool(decision['should_close']) or row['symbol'] not in target_symbols
                if not should_close:
                    continue
                amount = float(current_price) * int(row['quantity'])
                pnl = amount - float(row['cost_basis'])
                cash += amount
                exit_note = f"auto_{decision['reason']}"
                conn.execute(
                    """
                    UPDATE strategy_portfolio_positions
                    SET status = 'closed', closed_trade_date = ?, exit_price = ?, realized_pnl = ?
                    WHERE id = ?
                    """,
                    (trade_date, current_price, pnl, row['id']),
                )
                conn.execute(
                    """
                    INSERT INTO strategy_portfolio_trades (portfolio_key, trade_date, symbol, name, side, price, quantity, amount, note)
                    VALUES (?, ?, ?, ?, 'sell', ?, ?, ?, ?)
                    """,
                    (key, trade_date, row['symbol'], row['name'], current_price, row['quantity'], amount, exit_note),
                )

            existing_open = {
                row['symbol'] for row in conn.execute(
                    "SELECT symbol FROM strategy_portfolio_positions WHERE portfolio_key = ? AND status = 'open'",
                    (key,),
                ).fetchall()
            }
            for target in targets:
                if target['symbol'] in existing_open:
                    continue
                current_price = price_map.get(target['symbol']) or 0
                if current_price <= 0:
                    continue
                quantity = int(per_position_budget // current_price)
                if quantity <= 0:
                    continue
                amount = round(quantity * current_price, 2)
                if amount > cash:
                    continue
                cash -= amount
                conn.execute(
                    """
                    INSERT INTO strategy_portfolio_positions (
                        portfolio_key, symbol, name, opened_trade_date, entry_price, quantity, cost_basis, status, theme, signal_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?, ?)
                    """,
                    (
                        key,
                        target['symbol'],
                        target['name'],
                        trade_date,
                        current_price,
                        quantity,
                        amount,
                        target.get('theme', ''),
                        json.dumps(target, ensure_ascii=False),
                    ),
                )
                conn.execute(
                    """
                    INSERT INTO strategy_portfolio_trades (portfolio_key, trade_date, symbol, name, side, price, quantity, amount, note)
                    VALUES (?, ?, ?, ?, 'buy', ?, ?, ?, ?)
                    """,
                    (key, trade_date, target['symbol'], target['name'], current_price, quantity, amount, 'auto_portfolio_entry'),
                )

            refreshed_positions = [dict(row) for row in conn.execute(
                "SELECT * FROM strategy_portfolio_positions WHERE portfolio_key = ? AND status = 'open' ORDER BY id ASC",
                (key,),
            ).fetchall()]
            market_value = 0.0
            for row in refreshed_positions:
                current_price = price_map.get(row['symbol']) or row['entry_price']
                market_value += float(current_price) * int(row['quantity'])
            nav = round(cash + market_value, 2)
            conn.execute(
                "UPDATE strategy_portfolios SET cash = ?, nav = ?, updated_at = CURRENT_TIMESTAMP WHERE portfolio_key = ?",
                (round(cash, 2), nav, key),
            )
            conn.execute(
                """
                INSERT INTO strategy_portfolio_nav_history (portfolio_key, trade_date, nav, cash, market_value, note)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (key, trade_date, nav, round(cash, 2), round(market_value, 2), 'auto_rebalance'),
            )

    return strategy_portfolio_summary(limit=20)


def strategy_portfolio_summary(limit: int = 20) -> dict[str, Any]:
    bootstrap_strategy_portfolios()
    with get_conn() as conn:
        portfolios = []
        for row in conn.execute('SELECT * FROM strategy_portfolios ORDER BY id ASC').fetchall():
            item = dict(row)
            config = json.loads(item['config_json'])
            positions = [dict(p) for p in conn.execute(
                "SELECT * FROM strategy_portfolio_positions WHERE portfolio_key = ? AND status = 'open' ORDER BY id DESC",
                (item['portfolio_key'],),
            ).fetchall()]
            trades = [dict(t) for t in conn.execute(
                "SELECT * FROM strategy_portfolio_trades WHERE portfolio_key = ? ORDER BY id DESC LIMIT ?",
                (item['portfolio_key'], limit),
            ).fetchall()]
            history = [dict(h) for h in conn.execute(
                "SELECT * FROM strategy_portfolio_nav_history WHERE portfolio_key = ? ORDER BY id DESC LIMIT ?",
                (item['portfolio_key'], limit),
            ).fetchall()]
            nav = float(item['nav'])
            initial = float(item['initial_capital'])
            total_return_pct = round((nav / initial - 1) * 100, 2) if initial else 0.0
            item.update(
                {
                    'display_name': item['name'],
                    'description': config.get('description', ''),
                    'styles': config.get('styles', {}),
                    'positions': positions,
                    'recent_trades': trades,
                    'nav_history': history,
                    'position_count': len(positions),
                    'total_return_pct': total_return_pct,
                }
            )
            portfolios.append(item)
        return {
            'portfolio_count': len(portfolios),
            'initial_capital_per_portfolio': INITIAL_CAPITAL,
            'items': portfolios,
        }
