#!/bin/bash
# Run all end-of-day analysis jobs (compute layer, no Flask HTTP).
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

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

if [ -n "${SERVICE_SETTINGS:-}" ]; then
  :
elif [ -f "${TW_ANALYSIS_CONFIG_FILE:-$ROOT_DIR/analysis/config.ini}" ]; then
  export TW_ANALYSIS_CONFIG_FILE="${TW_ANALYSIS_CONFIG_FILE:-$ROOT_DIR/analysis/config.ini}"
  export TW_ANALYSIS_ENV="${TW_ANALYSIS_ENV:-local}"
fi

exec python -m compute eod_all
