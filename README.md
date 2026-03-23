# Quant Harness

A-share tactical research and closed-loop execution MVP.

## What this is

This project is a **research-first quantitative harness** for:

- market sentiment analysis
- leader-stock candidate selection
- hot-money / 龙虎榜 tracking
- daily closed-loop report generation
- paper-trading ready signal pipeline

It is intentionally **not** a fully automated live trading bot in v1.

## MVP goals

- Pull market/sample data
- Compute strategy features
- Generate candidate signals
- Summarize results into a daily report
- Expose APIs for a frontend dashboard
- Support future backtesting / paper trading / broker adapters

## Tech stack

### Backend
- Python 3.9+
- FastAPI
- Pydantic
- pandas
- httpx

### Frontend
- Next.js
- React
- TypeScript

## Project structure

```bash
quant-harness/
  apps/
    api/        # FastAPI backend
    web/        # Next.js dashboard
  packages/
    python/
      core/
      data/
      strategies/
      reports/
      execution/
  data/
    sample/
  scripts/
```

## Quick start

### 1. Backend

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8010
```

### 2. Frontend

```bash
cd apps/web
npm install
npm run dev
```

Then open:
- API: http://localhost:8010
- Web: http://localhost:3010

## API endpoints

- `GET /health`
- `GET /api/market/overview`
- `GET /api/signals`
- `GET /api/report/daily`
- `POST /api/pipeline/run`

## Notes

Current version uses sample data + deterministic scoring so the system is runnable immediately.
You can later swap in real collectors from AkShare / Tushare / 东方财富 / exchange data.

## Next expansion ideas

- Real data collectors
- DuckDB/Postgres storage
- Backtesting engine
- Paper trading
- Risk engine
- LLM-generated daily narrative
