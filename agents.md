# AGENTS.md

Guidance for AI agents and contributors working in the Twelvewin repository.

## Project Summary

Twelvewin is an **open-source A-share end-of-day quantitative research terminal** (Apache 2.0).

The **supported OSS stack** is:

1. **`compute/` + `jobs/` + `analysis/`** — offline pipelines; publish results to Postgres.
2. **`api/`** — FastAPI **Research API** (read-only analysis endpoints; no Flask import).
3. **`web/`** — Next.js **research terminal UI** (fundamentals, technical, clusters, stock detail).

Legacy **`app/`** (Flask + Jinja + Flask-Login) remains for backward compatibility but is **not** the target for new OSS features.

**Commercial edition** (accounts, billing, cloud hosting, watchlist sync) is developed separately and is **out of scope** for this repo.

## License

- Root [`LICENSE`](LICENSE): **Apache License 2.0**
- Do not add proprietary-licensed code to the main OSS tree without explicit separation.

## Primary Entry Points

### OSS runtime (preferred)

| Component | Entry | Port |
|-----------|--------|------|
| Compute CLI | `python -m compute eod_all` | — |
| Research API | `uvicorn api.main:app --port 8090` | 8090 |
| Web terminal | `cd web && npm run dev` | 3000 |
| Docker stack | `docker compose up -d --build` | 3000 / 8090 |

See [`docs/DOCKER.md`](docs/DOCKER.md) and [`.env.docker.example`](.env.docker.example).

### Database migrations

```bash
export FLASK_APP=manage.py TWELVEWIN_DISABLE_ANALYZER=1
flask db upgrade
```

Migrations live in `migrations/`. Compute-side schema checks: `core/schema.py`.

### Legacy Flask (maintenance only)

- [`manage.py`](manage.py) — `runserver`, `create_db`, `test`
- [`app/__init__.py`](app/__init__.py) — Flask app, blueprints, `Analyzer`, Redis
- [`start_dev.sh`](start_dev.sh) / [`start.sh`](start.sh) — legacy startup

Do **not** add new product features to Flask unless explicitly asked to maintain legacy parity.

## Architecture & Data Flow

```text
analysis/ + jobs/ + compute/
        → publish → Postgres (analysis_runs, ranking_results, daily_bars, …)
        → api/services/* (read)
        → web/lib/api.ts (fetch)
        → web/app/(dashboard)/*
```

Optional: **Redis** for live quotes (`REDIS_URL`); **CSV mirrors** when `TW_WRITE_RESULT_CSV=1`.

Default read path: **`READ_ANALYSIS_FROM_DB=true`** — Web/API read published DB rows, not raw CSV.

### Response contracts

Research API and legacy Flask AJAX share table shapes:

- `{ total, rows, updateTime, error? }`
- Ranking row fields often include: `code`, `name`, `per`, `pb`, `roe`, `close`, `rate`, `valueprice`, …

Preserve column names and response shapes unless all consumers (API tests, `web/`, legacy Flask) are updated together.

## Directory Guide

### `compute/`, `jobs/`, `analysis/`

- Batch / EOD logic, market data providers, technical screens, clustering, valuation.
- Publish via `compute/publish.py` → Postgres.
- Long-running; require `requirements-analysis.txt`.

### `core/`

- Shared DB engine (`core/db.py`), env loading (`core/env.py`), artifact keys (`core/artifacts.py`), schema helpers.

### `api/`

- FastAPI app: [`api/main.py`](api/main.py)
- Routers: rankings, fundamentals, technical, business, clusters, stocks, data-status
- Services read Postgres via `api/db/models.py` (ORM separate from Flask models but same tables)

### `web/`

- Next.js App Router, Tailwind v4, TanStack Table
- Key routes: `/fundamentals`, `/technical/*`, `/business`, `/clusters/*`, `/stock/[code]`
- `/login`, `/register` are placeholders — **no OSS auth backend yet**
- API client: [`web/lib/api.ts`](web/lib/api.ts); rewrites in [`web/next.config.ts`](web/next.config.ts)
- Design tokens: [`web/app/globals.css`](web/app/globals.css), [`DESIGN.md`](DESIGN.md)

### `app/` (legacy)

Flask blueprints: `stock/`, `technical_analysis/`, `user/`, `self_selected_stock/`, etc.

User/watchlist code here is **legacy**; future account features belong in a commercial repo, not OSS Flask.

### `docker/`

- [`docker-compose.yml`](docker-compose.yml) — Postgres, Redis, migrate, api, web; `jobs` profile for `eod`
- [`docker/api/Dockerfile`](docker/api/Dockerfile), [`docker/web/Dockerfile`](docker/web/Dockerfile), [`docker/python/Dockerfile`](docker/python/Dockerfile)

### `tests/`

Unit tests under `tests/` (API, publish, day_bars, services, config). Run:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Configuration

- Root [`.env.example`](.env.example) — `DATABASE_URL`, `REDIS_URL`, market data `TW_*`, `TUSHARE_TOKEN`
- Docker: [`.env.docker.example`](.env.docker.example)
- Web: [`web/.env.example`](web/.env.example) — `API_URL`
- Flask config: [`app/config.py`](app/config.py) via `APP_ENV` / `APP_SETTINGS`

## Safe Change Strategy

1. Identify **OSS vs legacy vs commercial** scope before coding.
2. Trace data: **Postgres published tables** first; CSV/Redis second.
3. For UI changes: `web/app/...` + matching `api/routers/...` + compute producer if fields change.
4. Keep diffs minimal; match existing style in each layer.
5. Do not commit `.env`, secrets, or `local_data/`.

### If editing the research terminal (web)

- Page: `web/app/(dashboard)/...`
- Components: `web/components/`
- Types / API: `web/lib/types.ts`, `web/lib/api.ts`
- Verify: `cd web && npm run build -- --webpack`

### If editing Research API

- Router: `api/routers/`
- Service: `api/services/`
- Tests: `tests/test_api.py` and related
- Verify: `uvicorn api.main:app` + `/docs`

### If editing analysis / compute

- Pipeline: `jobs/*_pipeline.py`, `compute/__main__.py`
- Logic: `analysis/*.py`
- Publish path: `compute/publish.py`, `analysis/result_export.py`
- Verify: `python -m compute eod_all` (or scoped job) + DB row counts / `GET /api/v1/data-status`

### If editing legacy Flask

- Only when maintaining old deployments or migrating behavior to API/web.
- Check blueprint `views.py` + Jinja template + CSV/DB service.

### If asked about auth / subscriptions / watchlist cloud sync

- Explain these are **commercial / Phase 3**, not in OSS scope.
- OSS web login pages are placeholders.

## Known Risks

- **Dual stack**: Flask and api/web may duplicate behavior — prefer api/web for new work.
- **Dual ORM**: `app/models.py` vs `api/db/models.py` — same DB, keep schema in sync via migrations.
- **`compute/publish.py` imports `app.models`** — Python job image needs Flask-SQLAlchemy deps (see `docker/python/Dockerfile`).
- **Partial Python 2 heritage** in older `analysis/` files — verify Python 3 syntax before running.
- **Market data jobs** need network + credentials; failures show as empty UI tables.
- **`TradingAgents-main/`** is vendored/third-party — not part of OSS product surface; exclude from Docker builds.

## Recommended First Checks

Before making changes, read as needed:

- [`README.md`](README.md)
- [`docs/DOCKER.md`](docs/DOCKER.md)
- [`api/README.md`](api/README.md)
- [`web/README.md`](web/README.md)
- [`docs/menu-pages-data-sources.md`](docs/menu-pages-data-sources.md)
- Relevant router/service and upstream pipeline for the feature

## Bottom Line

Treat this repository as an **Apache 2.0 OSS research terminal**: **compute publishes, API serves read-only analysis, web displays**. Flask is legacy. User management and monetization are **not** part of the open-source edition. Prefer small, contract-preserving changes in the api/web/compute path.
