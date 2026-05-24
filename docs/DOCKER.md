# Docker deployment (Twelvewin OSS)

Self-host the open-source stack with Docker Compose:

- **PostgreSQL** — analysis results and schema migrations
- **Redis** — optional live quotes for stock charts
- **Research API** — FastAPI (`api/`), port `8090`
- **Web Terminal** — Next.js (`web/`), port `3000`

Legacy Flask UI is not included in this compose file. Use the Research API + Web Terminal as the supported OSS surface.

## Prerequisites

- Docker Engine 24+ and Docker Compose v2
- ~4 GB disk for images and Postgres volume
- For compute jobs: network access and market data credentials (Tushare / AkShare)

## Quick start

```bash
git clone <YOUR_REPO_URL> twelvewin
cd twelvewin

cp .env.docker.example .env
# Edit .env: set SECRET_KEY, SECURITY_PASSWORD_SALT, and optional TUSHARE_TOKEN

docker compose up -d --build
```

Open:

- Web terminal: http://localhost:3000
- API docs: http://localhost:8090/docs
- Health: http://localhost:8090/api/v1/health

The UI will show empty tables until analysis data is published (see below).

## Publish analysis data

Run the end-of-day pipeline in a one-off container:

```bash
docker compose --profile jobs run --rm eod
```

Or only refresh rankings:

```bash
docker compose --profile jobs run --rm ranking
```

Ensure `.env` contains valid market data settings (`TUSHARE_TOKEN`, `TW_MARKET_DATA_PROVIDER`, etc.).

## Services

| Service  | Image build              | Port  | Role                          |
|----------|--------------------------|-------|-------------------------------|
| postgres | `postgres:16-alpine`     | 5432  | Database                      |
| redis    | `redis:7-alpine`         | 6379  | Quote cache                   |
| migrate  | `docker/python/Dockerfile` | —   | `flask db upgrade` (one-shot) |
| api      | `docker/api/Dockerfile`  | 8090  | Research API                  |
| web      | `docker/web/Dockerfile`  | 3000  | Next.js terminal              |
| eod      | `docker/python/Dockerfile` | —   | `python -m compute eod_all`   |

## File layout

```text
docker/
├── api/Dockerfile          # FastAPI service
├── web/Dockerfile          # Next.js production build
└── python/Dockerfile       # Migrations + compute jobs
docker-compose.yml
.env.docker.example
LICENSE                     # Apache 2.0
```

## Configuration

Compose injects in-network URLs:

- `DATABASE_URL=postgresql+psycopg://twelvewin:twelvewin@postgres:5432/twelvewin`
- `REDIS_URL=redis://redis:6379/0`
- `API_URL=http://api:8090` (web → api rewrites)

Override secrets in `.env` at the repository root. Do not commit `.env`.

## Development vs production

This compose file targets **local/self-hosted OSS** usage:

- Default Postgres credentials are for development only.
- Change `SECRET_KEY` and database passwords before exposing to the internet.
- Put a reverse proxy (nginx, Caddy) with TLS in front of `web` and `api` for production.

## Troubleshooting

**Empty fundamentals / rankings pages**

Run `docker compose --profile jobs run --rm eod` and check logs for market data errors.

**Migration failed**

```bash
docker compose run --rm migrate flask db upgrade
```

**Rebuild after code changes**

```bash
docker compose up -d --build
```

**Reset database**

```bash
docker compose down -v
docker compose up -d --build
```

## License

Twelvewin open-source components are licensed under the Apache License 2.0. See [LICENSE](../LICENSE).
