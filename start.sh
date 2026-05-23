#!/bin/bash
set -euo pipefail

if [ -f .env ]; then
  set -a
  # shellcheck source=/dev/null
  . ./.env
  set +a
fi

nohup python manage.py runserver -h 0.0.0.0 -p "${PORT:-8081}" &
