from __future__ import annotations

import os
from typing import Any

from packages.python.execution.pipeline import run_pipeline
from packages.python.report_archive import archive_daily_report
from packages.python.validation import validate_run


def run_daily_job() -> dict[str, Any]:
    payload = run_pipeline(persist=True, include_portfolio=False)
    run_id = payload["run_id"]
    validations = [] if os.getenv("VERCEL") else validate_run(run_id)
    result = {
        "run_id": run_id,
        "trade_date": payload["trade_date"],
        "source": payload["meta"]["source"],
        "signal_count": len(payload["signals"]),
        "validation_count": len(validations),
        "paper_execution": {
            "enabled": False,
            "execution_skipped": True,
            "reason": "线上轻量任务跳过模拟交易，避免 Vercel 函数超时。",
            "opened_count": 0,
            "closed_count": 0,
            "rebalanced_count": 0,
            "execution_policy": "research_only",
            "risk_mode": "research_only",
        },
        "strategy_portfolios": {
            "enabled": False,
            "reason": "线上轻量任务跳过多策略组合回测。",
        },
        "risk_gate": {
            "market_stage": payload["market"].get("market_sentiment_stage"),
            "risk_mode": "research_only",
            "execution_policy": "research_only",
            "no_trade": True,
            "notes": ["本次任务仅生成研究信号和日报，不执行模拟交易。"],
        },
        "report": payload["report"],
    }
    result["archive"] = archive_daily_report(result)
    return result
