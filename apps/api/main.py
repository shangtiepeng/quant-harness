from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from packages.python.execution.pipeline import run_pipeline


app = FastAPI(title="Quant Harness API", version="0.2.0")

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


@app.get("/api/signals")
def signals():
    payload = run_pipeline()
    return payload["signals"]


@app.get("/api/report/daily")
def daily_report():
    payload = run_pipeline()
    return payload["report"]


@app.post("/api/pipeline/run")
def pipeline_run():
    return run_pipeline()
