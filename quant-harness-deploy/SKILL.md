---
name: quant-harness-deploy
description: Use this skill when deploying the quant-harness / 极投雷达 project from the repository root to Vercel, including API and web deployments, required validation commands, Vercel project linking, environment variables, and known failure fixes.
---

# Quant Harness Deploy

Use this for deployment work in `/Users/hero/Documents/quant-harness`.

## Topology

- Frontend: `apps/web`, Vercel project `quant-harness-web`, production alias `https://herojiatou.com`.
- API: repository root, Vercel project `quant-harness-api-vercel`, production alias `https://api.herojiatou.com`.
- API entrypoint: `api/index.py` imports `apps.api.main:app`.
- API Vercel config: root `vercel.json`.
- Frontend Vercel config: `apps/web/vercel.json`.
- Production frontend env: `NEXT_PUBLIC_API_BASE_URL=https://api.herojiatou.com`.
- Production API env/config: `MARKET_DATA_PROVIDER_ORDER=sample` in root `vercel.json`.

## Safety Rules

- Never claim deployment succeeded until Vercel returns `readyState: READY` and the production alias is verified.
- Use the existing Vercel projects. Do not deploy `apps/web` into a new project named `web`.
- Keep `.vercel` directories untracked. They are ignored by root `.gitignore` and `apps/web/.gitignore`.
- The Vercel CLI may need these one-shot env vars on this machine:

```bash
NODE_TLS_REJECT_UNAUTHORIZED=0 npm_config_strict_ssl=false npm_config_ignore_scripts=true
```

This is only to work around local certificate / install-script issues while invoking Vercel CLI.

## Preflight

From repo root:

```bash
git status --short
git log -1 --oneline
source apps/api/.venv/bin/activate
python -m compileall -q api apps/api packages scripts
```

Frontend build:

```bash
cd apps/web
npm run build
```

API smoke test:

```bash
cd /Users/hero/Documents/quant-harness
source apps/api/.venv/bin/activate
MARKET_DATA_PROVIDER_ORDER=sample python - <<'PY'
from fastapi.testclient import TestClient
from apps.api.main import app
client = TestClient(app)
for path in ["/health", "/api/candidates", "/api/themes/heat?limit=3&market_limit=50"]:
    res = client.get(path)
    print(path, res.status_code)
    assert res.status_code == 200
PY
```

## Commit And Push

After validation:

```bash
git add <changed-files>
git commit -m "<concise Chinese commit message>"
git push origin main
```

If GitHub prints `This repository moved`, push can still succeed. Prefer checking `git status --short` and `git log -1 --oneline` after push.

## Deploy API

Run from repo root. First ensure it is linked to the API project:

```bash
NODE_TLS_REJECT_UNAUTHORIZED=0 npm_config_strict_ssl=false npm_config_ignore_scripts=true \
npm exec --yes --package=vercel -- vercel link --yes --project quant-harness-api-vercel
```

Deploy:

```bash
NODE_TLS_REJECT_UNAUTHORIZED=0 npm_config_strict_ssl=false npm_config_ignore_scripts=true \
npm exec --yes --package=vercel -- vercel deploy --prod --yes
```

Expected output includes:

- `Deploying missshang-heros-projects/quant-harness-api-vercel`
- `readyState: READY`
- `Aliased     https://api.herojiatou.com`

Verify:

```bash
curl -L --max-time 20 -sS https://api.herojiatou.com/health
curl -L --max-time 30 -sS 'https://api.herojiatou.com/api/themes/heat?limit=3&market_limit=50'
curl -L --max-time 30 -sS https://api.herojiatou.com/api/candidates
```

## Deploy Web

Run from `apps/web`. First ensure it is linked to the web project:

```bash
cd /Users/hero/Documents/quant-harness/apps/web
NODE_TLS_REJECT_UNAUTHORIZED=0 npm_config_strict_ssl=false npm_config_ignore_scripts=true \
npm exec --yes --package=vercel -- vercel link --yes --project quant-harness-web
```

Deploy:

```bash
NODE_TLS_REJECT_UNAUTHORIZED=0 npm_config_strict_ssl=false npm_config_ignore_scripts=true \
npm exec --yes --package=vercel -- vercel deploy --prod --yes --env NEXT_PUBLIC_API_BASE_URL=https://api.herojiatou.com
```

Expected output includes:

- `Deploying missshang-heros-projects/quant-harness-web`
- `readyState: READY`
- `Aliased     https://herojiatou.com`

Verify:

```bash
curl -L --max-time 30 -sS 'https://herojiatou.com/?deploy_check=<commit>' \
  | rg -o '极投雷达|题材热度分析与持续时间预测|选中题材持续性拆解|下一轮高增长' -n
```

## Known Failure Modes

### Vercel CLI says no credentials or certificate issuer error

Use:

```bash
NODE_TLS_REJECT_UNAUTHORIZED=0 npm_config_strict_ssl=false npm_config_ignore_scripts=true \
npm exec --yes --package=vercel -- vercel whoami
```

Complete the browser/device login if prompted.

### API returns fake old names

Check `data/sample/market_sample.json` and `/api/debug/raw-market`. Valid names should include searchable A-share names such as `埃斯顿`, `中际旭创`, `新易盛`, `中科曙光`, `科大讯飞`.

### API endpoint times out

Avoid routing simple endpoints through full `run_pipeline(include_portfolio=True)`. Use `include_portfolio=False` for dashboard basics. Heavy portfolio planning currently runs backtest/governor logic and may exceed Vercel limits.

### POST `/api/jobs/daily-run` returns 500

Vercel function filesystem is not writable except `/tmp`. Runtime DB and archives must use `/tmp` when `VERCEL` is set:

- `packages/python/storage.py`
- `packages/python/report_archive.py`

The online daily job should stay lightweight and skip external validation / simulated trading if needed.

### Web deploy goes to project `web`

This means `apps/web/.vercel/project.json` points to the wrong project. Re-link:

```bash
cd /Users/hero/Documents/quant-harness/apps/web
NODE_TLS_REJECT_UNAUTHORIZED=0 npm_config_strict_ssl=false npm_config_ignore_scripts=true \
npm exec --yes --package=vercel -- vercel link --yes --project quant-harness-web
```

Then deploy again.

## Final Deployment Checklist

- `npm run build` passed in `apps/web`.
- Python compile passed.
- API deployed and `https://api.herojiatou.com/health` returns `{"ok":true}`.
- Web deployed and `https://herojiatou.com` contains expected Chinese module text.
- `git status --short` is clean or only contains intentional untracked local artifacts.
- Final answer includes the production URLs and exact verification results.
