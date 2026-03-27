from __future__ import annotations

from math import sqrt
from statistics import mean, pstdev
from typing import Any

from packages.python.storage import get_conn, init_db


def _max_drawdown_pct(nav_series: list[float]) -> float:
    peak = None
    max_dd = 0.0
    for nav in nav_series:
        peak = nav if peak is None else max(peak, nav)
        if peak and peak > 0:
            dd = (nav / peak - 1) * 100
            max_dd = min(max_dd, dd)
    return round(max_dd, 2)


def _daily_returns(nav_series: list[float]) -> list[float]:
    if len(nav_series) < 2:
        return []
    returns: list[float] = []
    prev = nav_series[0]
    for nav in nav_series[1:]:
        if prev > 0:
            returns.append((nav / prev - 1) * 100)
        prev = nav
    return returns


def evaluate_strategy_portfolios(limit: int = 120) -> dict[str, Any]:
    init_db()
    with get_conn() as conn:
        portfolios = [dict(row) for row in conn.execute('SELECT * FROM strategy_portfolios ORDER BY id ASC').fetchall()]
        items: list[dict[str, Any]] = []
        for portfolio in portfolios:
            history = [dict(row) for row in conn.execute(
                'SELECT trade_date, nav, cash, market_value, note FROM strategy_portfolio_nav_history WHERE portfolio_key = ? ORDER BY trade_date ASC, id ASC LIMIT ?',
                (portfolio['portfolio_key'], limit),
            ).fetchall()]
            nav_series = [float(row['nav']) for row in history]
            daily_returns = _daily_returns(nav_series)
            avg_daily = round(mean(daily_returns), 3) if daily_returns else None
            vol_daily = round(pstdev(daily_returns), 3) if len(daily_returns) >= 2 else None
            sharpe_like = round((avg_daily / vol_daily) * sqrt(252), 3) if avg_daily is not None and vol_daily not in (None, 0) else None
            downside = [r for r in daily_returns if r < 0]
            downside_vol = round(pstdev(downside), 3) if len(downside) >= 2 else None
            sortino_like = round((avg_daily / downside_vol) * sqrt(252), 3) if avg_daily is not None and downside_vol not in (None, 0) else None
            total_return_pct = round((float(portfolio['nav']) / float(portfolio['initial_capital']) - 1) * 100, 2) if float(portfolio['initial_capital']) else 0.0
            item = {
                'portfolio_key': portfolio['portfolio_key'],
                'name': portfolio['name'],
                'nav': float(portfolio['nav']),
                'cash': float(portfolio['cash']),
                'initial_capital': float(portfolio['initial_capital']),
                'total_return_pct': total_return_pct,
                'max_drawdown_pct': _max_drawdown_pct(nav_series),
                'avg_daily_return_pct': avg_daily,
                'daily_volatility_pct': vol_daily,
                'sharpe_like': sharpe_like,
                'sortino_like': sortino_like,
                'nav_points': len(nav_series),
                'history': history[-30:],
            }
            items.append(item)

        ranked = sorted(items, key=lambda x: (x['total_return_pct'], -(abs(x['max_drawdown_pct']))), reverse=True)
        aggregate_nav = sum(item['nav'] for item in items)
        aggregate_initial = sum(item['initial_capital'] for item in items)
        return {
            'portfolio_count': len(items),
            'aggregate_nav': round(aggregate_nav, 2),
            'aggregate_initial_capital': round(aggregate_initial, 2),
            'aggregate_return_pct': round((aggregate_nav / aggregate_initial - 1) * 100, 2) if aggregate_initial else 0.0,
            'ranked': ranked,
        }
