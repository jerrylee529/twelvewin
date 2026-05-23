# Data contracts (compute ↔ web)

This directory defines the **published interfaces** between the offline compute layer
and the Flask web layer. Internal implementation may change; these contracts should not
break without a version bump.

## Ownership

| Domain | Writer | Reader | Primary store |
|--------|--------|--------|---------------|
| Stock master (`instrument`) | compute (`instruments.py`) | web (`Analyzer`, views) | Postgres `instrument` |
| Ranking screens (PE/PB/ROE/dividend/value) | compute (`ranking_pipeline`) | web (`ranking_service`) | Postgres `analysis_runs` + `ranking_results`; CSV backup |
| Fundamental screener | compute (`ranking_pipeline`) | API / Next web | Postgres `fundamental_snapshots` + `industry_fundamental_benchmarks` |
| Business screen | compute (`get_value_4_business`) | web (`business_service`) | Same as ranking, `result_key=business` |
| Technical screens | compute (`daily_pipeline`) | web (`technical_analysis_service`) | Postgres `technical_screen_results` |
| Price change | compute | web | `category=price_change` |
| Job status | compute (`compute` / `jobs` runner) | web (`data_status_service`) | Postgres `analysis_job_run` |
| User data (watchlist, labels) | web | web | Postgres |
| Intraday quotes | compute / legacy updater | web (`Analyzer.get_quotation`) | Redis hash by code |
| Daily bars | compute (`history_data_service` → `daily_bars`) | web (`daily_bar_service`) | Postgres `daily_bars` (optional CSV via `TW_WRITE_DAY_CSV`) |

## Versioning

- Git tag `v2.0.0` marks the baseline before compute/web package split.
- Contract changes should be noted in this folder and in release notes.

See [artifacts.md](artifacts.md) for CSV filenames and DB keys.
