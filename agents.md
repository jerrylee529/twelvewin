# agents.md

## Project Summary

This repository is a traditional Python stock-analysis web application centered on Flask.

- `app/` contains the web app, blueprints, templates, auth flow, Redis access, and SQLAlchemy models.
- `analysis/` contains offline analysis jobs, market data download logic, clustering, technical analysis, and scheduling scripts.
- `bin/` contains one-off or batch scripts for data download, report generation, prediction, and monitoring.
- `utils/` contains notification helpers such as mail and SMS utilities.

The product model is not a clean API-first service. It is a hybrid system:

1. Download and compute market/fundamental data offline.
2. Persist part of the data in MySQL and part of the outputs as CSV files.
3. Serve HTML pages and AJAX endpoints that read from both the database and the generated CSV artifacts.

## Current State

This codebase appears to be written primarily in Python 2 style, but the checked-in environment files are modernized only partially.

- Many files still use `reload(sys)`, `sys.setdefaultencoding(...)`, `print "..."`, and `except Exception, e`.
- `python --version` and `python3 --version` in the current workspace both resolve to Python 3.14.0.
- `requirements.txt` pins `Flask==3.1.3`, while several app patterns depend on old Flask extensions such as `Flask-Script` and older import conventions.

Assume the repository is in a partially migrated state. Before changing runtime behavior, verify whether the target task is meant to preserve legacy compatibility or continue a Python 3 migration.

## Primary Entry Points

### Web app

- [`manage.py`](/Users/jerrylee/Projects/twelvewin/manage.py)
  - Main management entry.
  - Exposes `runserver`, `db`, `create_db`, `drop_db`, `create_admin`, and `test`.
- [`app/__init__.py`](/Users/jerrylee/Projects/twelvewin/app/__init__.py)
  - Creates Flask app.
  - Loads config from `APP_SETTINGS`.
  - Initializes logging, Redis pool, SQLAlchemy, login manager, mail, bootstrap, and `Analyzer`.
  - Registers all blueprints.

### Startup scripts

- [`start_dev.sh`](/Users/jerrylee/Projects/twelvewin/start_dev.sh)
  - Sets `APP_SETTINGS=app.config.DevelopmentConfig`.
  - Runs the Flask dev server on port `8088`.
- [`start.sh`](/Users/jerrylee/Projects/twelvewin/start.sh)
  - Sets `APP_SETTINGS=app.config.ProductionConfig`.
  - Starts `manage.py runserver` in the background on port `8081`.
- [`start_uwsgi.sh`](/Users/jerrylee/Projects/twelvewin/start_uwsgi.sh)
  - Starts uWSGI with [`uwsgiconfig.ini`](/Users/jerrylee/Projects/twelvewin/uwsgiconfig.ini).

### Analysis jobs

- [`analysis/schedule_job.py`](/Users/jerrylee/Projects/twelvewin/analysis/schedule_job.py)
  - Orchestrates daily history download and technical-analysis result generation.
- [`analysis/history_data_service.py`](/Users/jerrylee/Projects/twelvewin/analysis/history_data_service.py)
  - Incrementally downloads daily history files.
- [`analysis/technical_analysis_service.py`](/Users/jerrylee/Projects/twelvewin/analysis/technical_analysis_service.py)
  - Generates result CSVs such as historical high/low and moving-average screens.

## Configuration Model

### Web app config

- [`app/config.py`](/Users/jerrylee/Projects/twelvewin/app/config.py)
  - `DevelopmentConfig` points to local MySQL: `mysql://root:password@127.0.0.1/stock?charset=utf8`
  - `ProductionConfig` reads from [`app/config/production.cfg`](/Users/jerrylee/Projects/twelvewin/app/config/production.cfg)
  - Mail, DB, and secret settings are defined here.

Required assumptions in the app:

- `APP_SETTINGS` must be set.
- Redis must be configured through `REDIS_URL`.
- SQLAlchemy must be able to connect at startup.
- Several routes assume `DAY_FILE_PATH` and `RESULT_PATH` exist in config and contain data files.

### Analysis config

- [`analysis/config.py`](/Users/jerrylee/Projects/twelvewin/analysis/config.py)
  - Reads config from `TW_ANALYSIS_CONFIG_FILE`
  - Chooses section with `TW_ANALYSIS_ENV`
  - Exposes paths such as `DAY_FILE_PATH` and `RESULT_FILE_PATH`

Important: the web app and the analysis scripts are tightly coupled through shared filesystem outputs. If analysis output paths move, web pages will break unless the app config is updated to the same locations.

## Directory Guide

### `app/`

Main Flask application.

- `main/`
  - Homepage, instrument search, profile data, prediction UI, investment knowledge, and exam endpoints.
- `user/`
  - Register, login, logout, confirmation, password reset.
- `stock/`
  - Fundamental ranking pages and candlestick/chart data.
- `business/`
  - Curated stock list built from generated CSV plus DB-backed labels.
- `technical_analysis/`
  - Technical-analysis ranking/filter pages.
- `strategy_analysis/`
  - Strategy result pages.
- `industry_analysis/`
  - Industry-level data and labeling.
- `cluster_analysis/`
  - Cluster result pages.
- `self_selected_stock/`
  - User watchlist management.
- `annual_report/`
  - Annual report and stock/industry performance pages.
- `templates/`
  - Server-rendered Jinja templates.
- `static/`
  - CSS/JS assets, including chart rendering with ECharts.

### `analysis/`

Offline data and quantitative processing.

- Downloads instrument lists and daily data.
- Computes technical analysis outputs into CSV files.
- Performs clustering and prediction-related work.
- Contains ad hoc scripts and some backup or experimental files such as `.bak` and `.old`.

### `bin/`

Standalone scripts for:

- downloading history or index data
- prediction dataset generation
- business report generation
- monitoring and alerting
- strategy experimentation

Treat `bin/` as utility scripts, not as a coherent library layer.

## Core Data Flow

### Database-backed data

Defined mainly in [`app/models.py`](/Users/jerrylee/Projects/twelvewin/app/models.py).

Important entities include:

- `User`
- `SelfSelectedStock`
- `Instrument`
- `Report`
- `StockLabels`
- `StockCluster` / `StockClusterItem`
- `StockPrediction`
- additional finance/report models further down the file

### File-backed data

A large part of the UI depends on generated CSV files.

Examples:

- `stock_pe.csv`
- `stock_pb.csv`
- `stock_roe.csv`
- `stock_dividence.csv`
- `stock_business.csv`
- `highest_in_history.csv`
- `lowest_in_history.csv`
- `ma_long.csv`
- per-stock history files under `DAY_FILE_PATH`, typically `<code>.csv`

If a page looks broken but the route code is simple, check the corresponding CSV artifact first.

### Redis-backed realtime quote data

- [`app/redis_op.py`](/Users/jerrylee/Projects/twelvewin/app/redis_op.py)
- `Analyzer.get_quotation()` reads Redis hash data by stock code.
- Candlestick/profile/prediction pages use Redis to supplement or freshen historical file data.

## Web Surface Map

Representative routes:

- `/` home page
- `/main/instruments` instrument autocomplete data
- `/main/profile/<code>` finance/profile JSON
- `/main/predict` prediction page flow
- `/<path>` stock ranking pages such as `pe`, `pb`, `roe`, `divi`, `business`
- `/<path>/data` corresponding ranking JSON
- `/candlestick/<code>` K-line page
- `/candlestick/<code>/hq` candlestick data
- `/selfselectedstock` watchlist page
- `/selfselectedstock/data` watchlist data
- `/industry`, `/industry/data`, `/industry/stock/<code>` industry analysis
- `/cluster/...` clustering results
- `/tech/...` technical analysis
- `/annual_report/...` annual report related pages

When modifying a page, check both the Jinja template and the paired AJAX endpoint. Most pages are split that way.

## Important Couplings

1. `app/__init__.py` eagerly constructs `Analyzer` at import time.
   - Startup can fail if DB/config is incomplete.
   - `Analyzer` also preloads instrument data.

2. Many views read CSV files directly from configured paths.
   - A schema or filename change in analysis scripts can silently break the UI.

3. The code mixes database truth and file truth.
   - Example: watchlist labels are in DB, rankings are in CSV, realtime quotes are in Redis.

4. The codebase uses legacy absolute imports in several places.
   - Example: `from redis_op import RedisOP`, `from analyzer import Analyzer`
   - Be careful when changing package layout.

## Known Risks

- No `tests/` directory is present, although `manage.py test` expects one.
- The Python version story is inconsistent.
- Some code in `analysis/` appears stale or syntactically broken for Python 3.
- There are backup files (`.bak`, `.old`) inside live directories.
- Some endpoints do direct file I/O without much validation or error handling.
- Redis URL parsing is custom and narrow.
- App startup relies on environment variables being present before import.

## Safe Change Strategy

When working in this repository, prefer the following order:

1. Identify whether the target behavior is database-backed, CSV-backed, or Redis-backed.
2. Trace the route to the template and the paired JSON endpoint.
3. Trace the data source to either:
   - `app/models.py`
   - an analysis script under `analysis/`
   - a generated CSV under `RESULT_PATH` or `DAY_FILE_PATH`
4. Preserve legacy filenames and response shapes unless you also update every consumer.
5. Avoid broad refactors unless the task explicitly asks for modernization.

## Change Guidance By Area

### If editing web pages

- Check the template in `app/templates/...`
- Check the paired blueprint route in `app/*/views.py`
- Check whether the page reads JSON from a `/data` endpoint
- Confirm the expected columns in the underlying CSV or SQL model

### If editing analysis logic

- Verify input path config first
- Verify output filenames used by the UI
- Keep CSV column names stable unless all readers are updated
- Expect long-running, batch-style execution

### If editing auth or user flows

- Check `app/user/views.py`, `app/user/forms.py`, `app/token.py`, `app/myemail.py`
- Email confirmation and password reset are part of the normal account flow

### If editing market data or charts

- Check `app/stock/views.py`
- Check `Analyzer` methods in [`app/analyzer.py`](/Users/jerrylee/Projects/twelvewin/app/analyzer.py)
- Check Redis quote structure and day-history CSV format together

## Verification Guidance

There is no reliable built-in automated test suite in the current repo state.

Preferred verification is manual and scoped:

- import/startup sanity for the touched module
- route-level smoke test for changed endpoints
- template render smoke test for changed pages
- spot-check the expected CSV or DB records exist

If you need to modernize code, do it in small slices and verify one execution path at a time.

## Recommended First Checks For Any Future Agent

Before making changes, inspect:

- [`README.md`](/Users/jerrylee/Projects/twelvewin/README.md)
- [`manage.py`](/Users/jerrylee/Projects/twelvewin/manage.py)
- [`app/__init__.py`](/Users/jerrylee/Projects/twelvewin/app/__init__.py)
- [`app/config.py`](/Users/jerrylee/Projects/twelvewin/app/config.py)
- the relevant blueprint `views.py`
- the upstream analysis script or CSV producer for that feature

## Bottom Line

Treat this repository as a legacy Flask + MySQL + Redis + CSV analytics system with significant Python 2 heritage and partial Python 3-era dependency updates. Small, local, compatibility-preserving changes are low risk. Broad runtime, dependency, or packaging changes should be approached as deliberate migration work, not incidental cleanup.
