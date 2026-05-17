#!/bin/bash
set -euo pipefail

export APP_SETTINGS="${APP_SETTINGS:-app.config.LocalConfig}"

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

exec ./.venv312/bin/python manage.py runserver -h 0.0.0.0 -p "${PORT:-8088}"
