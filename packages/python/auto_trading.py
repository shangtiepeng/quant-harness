from __future__ import annotations

from typing import Any

from packages.python.data.real_collectors import load_market_data
from packages.python.execution.pipeline import run_pipeline
from packages.python.paper_execution import (
    list_paper_positions,
    list_paper_trades,
    paper_portfolio_summary,
    run_paper_execution,
)
from packages.python.strategy_portfolios import run_strategy_portfolios, strategy_portfolio_summary


EXECUTION_MODES = {
    'paper_only',
    'strategy_portfolios',
    'hybrid',
}


def _normalize_mode(mode: str | None) -> str:
    value = str(mode or 'hybrid').strip().lower()
    return value if value in EXECUTION_MODES else 'hybrid'


def auto_trade_snapshot(mode: str | None = None, limit: int = 50) -> dict[str, Any]:
    normalized_mode = _normalize_mode(mode)
    payload = run_pipeline(limit=limit)
    market_stocks, market_meta = load_market_data(limit=limit)
    stocks = [s.model_dump() for s in market_stocks]

    paper_summary = paper_portfolio_summary(stocks)
    strategy_summary = strategy_portfolio_summary(limit=10)

    return {
        'mode': normalized_mode,
        'trade_date': payload['trade_date'],
        'market': payload['market'],
        'meta': {
            'pipeline_source': payload['meta'].get('source'),
            'price_source': market_meta.get('source'),
            'candidate_count': len(payload.get('candidates') or []),
            'signal_count': len(payload.get('signals') or []),
        },
        'portfolio_plan': payload['portfolio_plan'],
        'paper_trading': {
            'summary': paper_summary,
            'positions': list_paper_positions(),
            'recent_trades': list_paper_trades(limit=20),
        },
        'strategy_portfolios': strategy_summary,
    }


def run_auto_trading(mode: str | None = None, limit: int = 50) -> dict[str, Any]:
    normalized_mode = _normalize_mode(mode)
    payload = run_pipeline(limit=limit, persist=True)
    market_stocks, market_meta = load_market_data(limit=limit)
    stocks = [s.model_dump() for s in market_stocks]

    paper_result: dict[str, Any] = {
        'enabled': False,
        'execution_skipped': True,
        'reason': 'mode_disabled',
    }
    strategy_result: dict[str, Any] = {
        'enabled': False,
        'reason': 'mode_disabled',
    }

    if normalized_mode in {'paper_only', 'hybrid'}:
        paper_result = {
            'enabled': True,
            **run_paper_execution(payload, stocks),
            'summary': paper_portfolio_summary(stocks),
            'positions': list_paper_positions(),
            'recent_trades': list_paper_trades(limit=20),
        }

    if normalized_mode in {'strategy_portfolios', 'hybrid'}:
        strategy_summary = run_strategy_portfolios()
        strategy_result = {
            'enabled': True,
            'summary': strategy_summary,
        }

    risk_gate = {
        'market_stage': payload['portfolio_plan'].get('market_stage'),
        'risk_mode': payload['portfolio_plan'].get('risk_mode'),
        'execution_policy': payload['portfolio_plan'].get('execution_policy'),
        'no_trade': payload['portfolio_plan'].get('no_trade'),
        'notes': payload['portfolio_plan'].get('notes') or [],
    }

    return {
        'mode': normalized_mode,
        'run_id': payload.get('run_id'),
        'trade_date': payload['trade_date'],
        'meta': {
            'pipeline_source': payload['meta'].get('source'),
            'price_source': market_meta.get('source'),
            'candidate_count': len(payload.get('candidates') or []),
            'signal_count': len(payload.get('signals') or []),
        },
        'risk_gate': risk_gate,
        'portfolio_plan': payload['portfolio_plan'],
        'paper_trading': paper_result,
        'strategy_portfolios': strategy_result,
    }


def execution_control_matrix() -> dict[str, Any]:
    return {
        'supported_modes': [
            {
                'mode': 'paper_only',
                'label': '单账户纸面执行',
                'description': '按候选分配计划执行开平仓和调仓，不触发真实券商下单。',
            },
            {
                'mode': 'strategy_portfolios',
                'label': '多策略组合自动轮动',
                'description': '按预设组合风格自动调仓、记账和更新 NAV。',
            },
            {
                'mode': 'hybrid',
                'label': '混合模式',
                'description': '同时运行单账户纸面执行和多策略组合轮动，便于对照研究。',
            },
        ],
        'safety': {
            'broker_execution': False,
            'default_policy': 'paper_only',
            'guardrails': [
                '仅支持 paper trading / simulated execution',
                '市场情绪与风险预算先决于开仓动作',
                '低共振与弱角色候选将被自动过滤',
                '自动调仓仅在本地 sqlite 账本中生效',
            ],
        },
    }
