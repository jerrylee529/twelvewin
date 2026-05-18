#!/usr/bin/env bash

set -euo pipefail

export FLASK_APP="${FLASK_APP:-manage.py}"
PYTHON="${PYTHON:-./.venv312/bin/python}"
FLASK="${FLASK:-./.venv312/bin/flask}"

"$PYTHON" manage.py create_db
"$FLASK" db upgrade
