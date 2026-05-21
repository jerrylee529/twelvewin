# Artifact contracts

## Environment variables (compute + web)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | yes (prod) | Postgres URI; normalized to `postgresql+psycopg://` |
| `DAY_FILE_PATH` | compute | Directory of per-code daily CSV files |
| `RESULT_PATH` | compute | Directory of ranking / technical result CSV files |
| `READ_ANALYSIS_FROM_DB` | web | Default `true`; web reads Postgres before CSV fallback |
| `REDIS_URL` | web (quotes) | Realtime quote hashes |

Compute jobs must **not** depend on `APP_SETTINGS` or Flask import; use `python -m compute`
with `.env` sourced.

## Ranking CSV files (`RESULT_PATH`)

| UI key | Filename | `result_key` in DB |
|--------|----------|-------------------|
| `pe` | `stock_pe.csv` | `pe` |
| `pb` | `stock_pb.csv` | `pb` |
| `roe` | `stock_roe.csv` | `roe` |
| `divi` | `stock_dividence.csv` | `divi` |
| (value ranking) | `stock_value.csv` | (import as ranking when wired) |
| business | `stock_business.csv` | `business` |

Required columns (minimum): `code`, `name`. Additional numeric fields are stored in JSON `data`.

## Technical screen CSV files

| UI key | Filename |
|--------|----------|
| `highest` | `highest_in_history.csv` |
| `lowest` | `lowest_in_history.csv` |
| `ma_long` | `ma_long.csv` |
| `break_ma` | `break_ma.csv` |
| `above_ma` | `above_ma.csv` |
| price change | `price_change.csv` |

## Daily history files (`DAY_FILE_PATH`)

- Path pattern: `{DAY_FILE_PATH}/{code}.csv`
- Instrument list export: `{DAY_FILE_PATH}/instruments.csv` (`code`, `name`)

## Database publish model (phase 6)

After compute finishes CSV generation, `sync_results_to_db` inserts:

1. Row in `analysis_runs` (`category`, `result_key`, `as_of_date`, `row_count`, `source_file`)
2. Rows in `ranking_results` or `technical_screen_results` linked by `run_id`

Web reads the latest run per `(category, result_key)` ordered by `as_of_date` desc.

## Clustering (industry)

- **Writer**: offline `analysis/cluster_data_service.py` (future: dedicated compute job)
- **Reader**: web `cluster_analysis` views query `stock_cluster` / `stock_cluster_item` only
- Web must **not** invoke cluster computation on HTTP requests
