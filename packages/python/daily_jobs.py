from __future__ import annotations

from typing import Any

from packages.python.data.real_collectors import load_market_data
from packages.python.execution.pipeline import run_pipeline
from packages.python.paper_execution import run_paper_execution
from packages.python.report_archive import archive_daily_report
from packages.python.validation import validate_run


def run_daily_job() -> dict[str, Any]:
    payload = run_pipeline(persist=True)
    run_id = payload["run_id"]
    validations = validate_run(run_id)
    stocks, _meta = load_market_data(limit=50)
    paper_result = run_paper_execution(payload, [s.model_dump() for s in stocks])
    result = {
        "run_id": run_id,
        "trade_date": payload["trade_date"],
        "source": payload["meta"]["source"],
        "signal_count": len(payload["signals"]),
        "validation_count": len(validations),
        "paper_execution": paper_result,
        "report": payload["report"],
    }
    result["archive"] = archive_daily_report(result)
    return result
