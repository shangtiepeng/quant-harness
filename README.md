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

### Daily automation

Run one complete daily job manually:

```bash
cd /Users/hero/Documents/quant-harness
python3 scripts/run_daily_job.py
```

This will:
- run the pipeline
- persist the run
- validate saved signals
- print a daily summary JSON

Install a weekday cron job (16:05, Mon-Fri):

```bash
cd /Users/hero/Documents/quant-harness
./scripts/setup_cron.sh
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
- `GET /api/meta`
- `GET /api/market/overview`
- `GET /api/signals`
- `GET /api/report/daily`
- `POST /api/pipeline/run`  # persist one run into sqlite
- `POST /api/jobs/daily-run`  # run pipeline + validation as one job
- `GET /api/history/runs`
- `GET /api/history/runs/{run_id}/signals`
- `POST /api/history/runs/{run_id}/validate`
- `GET /api/history/validations`
- `GET /api/analytics/strategy-performance`

## Notes

Current version prefers **real market input when available**:
1. AkShare
2. Eastmoney public endpoint fallback
3. bundled sample data fallback

So the system remains runnable even if one source fails.

## Recommended route

The current implementation follows the most stable route:
- clean local repo hygiene
- connect real market data conservatively
- keep sample fallback for reliability
- generate a post-market daily loop first
- expand later into storage / backtest / paper trading

## Next expansion ideas

- Real data collectors
- DuckDB/Postgres storage
- Backtesting engine
- Paper trading
- Risk engine
- LLM-generated daily narrative
