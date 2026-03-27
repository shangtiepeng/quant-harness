from __future__ import annotations

from typing import Any

from packages.python.auto_trading import run_auto_trading
from packages.python.execution.pipeline import run_pipeline
from packages.python.report_archive import archive_daily_report
from packages.python.validation import validate_run


def run_daily_job() -> dict[str, Any]:
    payload = run_pipeline(persist=True)
    run_id = payload["run_id"]
    validations = validate_run(run_id)
    auto_trading = run_auto_trading(mode='hybrid')
    result = {
        "run_id": run_id,
        "trade_date": payload["trade_date"],
        "source": payload["meta"]["source"],
        "signal_count": len(payload["signals"]),
        "validation_count": len(validations),
        "paper_execution": auto_trading["paper_trading"],
        "strategy_portfolios": auto_trading["strategy_portfolios"],
        "risk_gate": auto_trading["risk_gate"],
        "report": payload["report"],
    }
    result["archive"] = archive_daily_report(result)
    return result
