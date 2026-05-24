# Twelvewin Web (Next.js)

Phase 2 frontend for the Twelvewin SaaS product. Consumes the FastAPI service in `../api/`.

## Prerequisites

1. Backend API running on port `8090`:

```bash
cd ..
uvicorn api.main:app --reload --port 8090
```

2. Published analysis data in Postgres (if tables are empty):

```bash
python -m compute eod_all
```

## Design

UI follows [`DESIGN.md`](../DESIGN.md) — **The Predictive Terminal** aesthetic:

- Deep navy tonal surfaces (no hard borders)
- Inter typography with tabular numbers for financial data
- Cyber gradient (cyan → purple) for primary actions
- Glass overlays for search dropdowns and auth panes
- High-density tables (`body-sm` / 12px)

Design tokens live in `app/globals.css`. Reusable primitives are in `components/ui/primitives.tsx`.

## Setup

```bash
cd web
cp .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000

## Environment

| Variable | Description |
|----------|-------------|
| `API_URL` | Backend origin for Next.js rewrites (default `http://127.0.0.1:8090`) |
| `NEXT_PUBLIC_API_URL` | Optional direct client-side API base; leave empty to use same-origin rewrites |

## MVP Routes

| Route | Description |
|-------|-------------|
| `/` | Marketing homepage + stock search |
| `/rankings/pe` | PE ranking table |
| `/rankings/pb` | PB ranking |
| `/rankings/roe` | ROE ranking |
| `/rankings/divi` | Dividend yield ranking |
| `/technical/*` | Technical screen pages |
| `/business` | Curated business list |
| `/clusters/sz50` | Index cluster view |
| `/stock/[code]` | Candlestick + finance profile |
| `/login`, `/register` | Placeholders for Phase 3 auth |

## Architecture

- **App Router** with server components fetching via `/api/v1/*` rewrites
- **TanStack Table** for ranking grids
- **lightweight-charts** for candlestick rendering
- Client components only where interactivity is required (search, charts, table pagination)
