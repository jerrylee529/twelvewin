#!/bin/bash
# Run all end-of-day analysis jobs (compute layer; config from .env via python-dotenv).
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

# Optional: shell-level export before Python starts (python-dotenv also loads .env).
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

exec python -m compute eod_all
