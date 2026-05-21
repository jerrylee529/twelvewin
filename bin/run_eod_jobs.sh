#!/bin/bash
# Run all end-of-day analysis jobs with DB run tracking.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

export TWELVEWIN_DISABLE_ANALYZER=1

if [ -f ".venv312/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv312/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

if [ -n "${SERVICE_SETTINGS:-}" ]; then
  :
elif [ -f "${TW_ANALYSIS_CONFIG_FILE:-$ROOT_DIR/analysis/config.ini}" ]; then
  export TW_ANALYSIS_CONFIG_FILE="${TW_ANALYSIS_CONFIG_FILE:-$ROOT_DIR/analysis/config.ini}"
  export TW_ANALYSIS_ENV="${TW_ANALYSIS_ENV:-local}"
else
  export APP_SETTINGS="${APP_SETTINGS:-app.config.LocalConfig}"
  export TWELVEWIN_DISABLE_ANALYZER=1
fi

python manage.py run_job eod_all
