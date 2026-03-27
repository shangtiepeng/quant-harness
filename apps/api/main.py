from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from collections import Counter

from packages.python.analytics import strategy_performance_summary
from packages.python.lifecycle_analytics import trade_lifecycle_summary
from packages.python.strategy_governor import build_strategy_governor
from packages.python.auto_trading import auto_trade_snapshot, execution_control_matrix, run_auto_trading
from packages.python.backtest import backtest_signals
from packages.python.daily_jobs import run_daily_job
from packages.python.execution.pipeline import run_pipeline
from packages.python.paper_execution import list_paper_positions, list_paper_trades, paper_portfolio_summary
from packages.python.report_archive import list_archived_reports, read_archived_report
from packages.python.resonance_analytics import resonance_validation_summary
from packages.python.storage import list_runs, list_signals_by_run, list_validations
from packages.python.strategy_portfolios import strategy_portfolio_summary
from packages.python.portfolio_evaluator import evaluate_strategy_portfolios
from packages.python.experiment_lab import run_experiment_lab
from packages.python.validation import validate_run
from packages.python.data.real_collectors import load_market_data


app = FastAPI(title="Quant Harness API", version="0.6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/meta")
def meta():
    payload = run_pipeline()
    return payload["meta"]


@app.get("/api/market/overview")
def market_overview():
    payload = run_pipeline()
    return payload["market"]


@app.get("/api/debug/raw-market")
def debug_raw_market(limit: int = 20):
    stocks, meta = load_market_data(limit=limit)
    return {
        "meta": meta,
        "items": [s.model_dump() for s in stocks],
    }


@app.get("/api/signals")
def signals():
    payload = run_pipeline()
    return payload["signals"]


@app.get("/api/candidates")
def candidates():
    payload = run_pipeline()
    return payload["candidates"]


@app.get("/api/portfolio-plan")
def portfolio_plan():
    payload = run_pipeline()
    return payload["portfolio_plan"]


@app.get("/api/paper/positions")
def paper_positions():
    return list_paper_positions()


@app.get("/api/paper/trades")
def paper_trades(limit: int = 100):
    return list_paper_trades(limit=limit)


@app.get("/api/paper/summary")
def paper_summary():
    payload = run_pipeline()
    market_stocks, _meta = load_market_data(limit=50)
    return {
        "portfolio": paper_portfolio_summary([s.model_dump() for s in market_stocks]),
        "plan": payload["portfolio_plan"],
        "candidate_count": len(payload.get("candidates") or []),
    }


@app.get("/api/auto-trading/meta")
def auto_trading_meta():
    return execution_control_matrix()


@app.get("/api/auto-trading/snapshot")
def auto_trading_snapshot(mode: str = "hybrid", limit: int = 50):
    return auto_trade_snapshot(mode=mode, limit=limit)


@app.post("/api/auto-trading/run")
def auto_trading_run(mode: str = "hybrid", limit: int = 50):
    return run_auto_trading(mode=mode, limit=limit)


@app.get("/api/strategy-portfolios/summary")
def strategy_portfolios_summary(limit: int = 20):
    return strategy_portfolio_summary(limit=limit)


@app.get("/api/strategy-portfolios/evaluator")
def strategy_portfolios_evaluator(limit: int = 120):
    return evaluate_strategy_portfolios(limit=limit)


@app.get("/api/themes/heat")
def themes_heat(limit: int = 10):
    stocks, meta = load_market_data(limit=50)
    counter: Counter[str] = Counter()
    score_map: dict[str, float] = {}
    leaders: dict[str, list[str]] = {}
    for stock in stocks:
        concepts = stock.concepts or ([stock.theme] if stock.theme else [])
        for idx, concept in enumerate(concepts[:3]):
            if not concept or concept == '题材待补全':
                continue
            weight = 1.0 if idx == 0 else 0.6 if idx == 1 else 0.3
            counter[concept] += 1
            score_map[concept] = score_map.get(concept, 0.0) + (
                weight * (1 + max(stock.pct_change, 0) / 10 + stock.volume_ratio / 5)
            )
            leaders.setdefault(concept, [])
            if len(leaders[concept]) < 3:
                leaders[concept].append(f"{stock.name}({stock.symbol})")
    ranked = sorted(counter.items(), key=lambda item: (score_map.get(item[0], 0), item[1]), reverse=True)
    return {
        "meta": meta,
        "items": [
            {
                "theme": theme,
                "count": count,
                "heat_score": round(score_map.get(theme, 0.0), 2),
                "is_mainline": index < 3,
                "leaders": leaders.get(theme, []),
            }
            for index, (theme, count) in enumerate(ranked[:limit])
        ],
    }


@app.get("/api/report/daily")
def daily_report():
    payload = run_pipeline()
    return payload["report"]


@app.post("/api/pipeline/run")
def pipeline_run():
    return run_pipeline(persist=True)


@app.post("/api/jobs/daily-run")
def jobs_daily_run():
    return run_daily_job()


@app.get("/api/history/runs")
def history_runs(limit: int = 20):
    return list_runs(limit=limit)


@app.get("/api/history/runs/{run_id}/signals")
def history_run_signals(run_id: int):
    return list_signals_by_run(run_id)


@app.post("/api/history/runs/{run_id}/validate")
def history_run_validate(run_id: int):
    return validate_run(run_id)


@app.get("/api/history/validations")
def history_validations(limit: int = 50):
    return list_validations(limit=limit)


@app.get("/api/history/reports")
def history_reports(limit: int = 30):
    return list_archived_reports(limit=limit)


@app.get("/api/history/reports/{trade_date}")
def history_report_detail(trade_date: str):
    return read_archived_report(trade_date)


@app.get("/api/analytics/strategy-performance")
def analytics_strategy_performance(limit: int = 500):
    return strategy_performance_summary(limit=limit)


@app.get("/api/analytics/backtest")
def analytics_backtest(limit: int = 50, kline_days: int = 30):
    return backtest_signals(limit=limit, kline_days=kline_days)


@app.get("/api/analytics/resonance-validation")
def analytics_resonance_validation(limit: int = 500):
    return resonance_validation_summary(limit=limit)


@app.get("/api/analytics/trade-lifecycle")
def analytics_trade_lifecycle(limit: int = 200):
    return trade_lifecycle_summary(limit=limit)


@app.get("/api/analytics/strategy-governor")
def analytics_strategy_governor(limit: int = 200):
    return build_strategy_governor(history_limit=limit)


@app.get("/api/analytics/experiment-lab")
def analytics_experiment_lab(limit: int = 160):
    return run_experiment_lab(limit=limit)


