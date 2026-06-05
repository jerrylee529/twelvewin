# Twelvewin REST API

Standalone FastAPI service for published analysis results. This package reads Postgres via `core/db.py` and does **not** import Flask.

## Setup

From the repository root:

```bash
python -m venv .venv-api
source .venv-api/bin/activate
pip install -r api/requirements.txt
```

Ensure `.env` contains `DATABASE_URL` (same as compute/web).

Optional:

- `API_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`
- `REDIS_URL=redis://127.0.0.1:6379/0` (for live quote bar on `/stocks/{code}/bars`)
- `TW_RESEARCH_API_KEY=` (when set, all `/api/v1/*` routes except `/health` require `X-Twelvewin-Api-Key`)

## Run

```bash
cd /path/to/twelvewin
uvicorn api.main:app --reload --port 8090
```

- Swagger UI: http://localhost:8090/docs
- Health: `GET /api/v1/health`
- PE ranking: `GET /api/v1/rankings/pe`
- Data status: `GET /api/v1/data-status`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Liveness check |
| GET | `/api/v1/data-status` | Artifact freshness and job status |
| GET | `/api/v1/rankings/{pe\|pb\|roe\|divi}` | Fundamental rankings |
| GET | `/api/v1/technical/{key}` | Technical screens |
| GET | `/api/v1/technical/filter/price-change` | Price change filter |
| GET | `/api/v1/business` | Curated business list |
| GET | `/api/v1/clusters/{section}` | Index/industry clusters |
| GET | `/api/v1/industries` | Industry list |
| GET | `/api/v1/industries/{name}/data` | Industry cluster table |
| GET | `/api/v1/industries/{name}/stocks/{code}` | Peers in same cluster |
| GET | `/api/v1/stocks/search?q=` | Instrument search |
| GET | `/api/v1/stocks/{code}/bars` | Candlestick OHLC rows |
| GET | `/api/v1/stocks/{code}/profile` | Finance profile + quote |
| GET | `/api/v1/stocks/{code}/research-context` | Aggregated research payload for Dify agent tools |

Optional header when `TW_RESEARCH_API_KEY` is set: `X-Twelvewin-Api-Key`.

Response shapes match the legacy Flask AJAX endpoints (`total`, `rows`, `updateTime`).

## Data prerequisite

Published rows must exist in Postgres:

```bash
python -m compute eod_all
```

Stock finance profile charts (`/stocks/{code}/profile`) are populated separately from Tushare Pro:

```bash
export TUSHARE_TOKEN=your-token
python -m compute finance_profile_pipeline
```

Optional env vars: `TW_FINANCE_PROFILE_YEARS` (default `5`), `TW_FINANCE_PROFILE_CODES`, `TW_FINANCE_PROFILE_MAX_CODES`, `TW_FINANCE_PROFILE_SLEEP_SEC`. Set `TW_RUN_FINANCE_PROFILE=1` to include this step in `eod_all`.

## Dify agent integration

When Twelvewin API runs on the host (`uvicorn :8090`) and Dify runs in Docker on the same machine, configure Dify tools to call `http://host.docker.internal:8090`, not `127.0.0.1`.

See [`deploy/dify/README.md`](../deploy/dify/README.md) for exact URLs, env vars, and HTTP tool paths.
