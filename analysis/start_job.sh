#!/bin/bash
# Legacy wrapper: prefer bin/run_eod_jobs.sh from the repository root.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

export SERVICE_SETTINGS="${SERVICE_SETTINGS:-analysis.config.ProductionConfig}"
export TWELVEWIN_DISABLE_ANALYZER=1

exec "$ROOT_DIR/bin/run_eod_jobs.sh"
