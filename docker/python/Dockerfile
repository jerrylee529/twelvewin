# Twelvewin Python runtime: DB migrations and offline compute jobs
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    TWELVEWIN_DISABLE_ANALYZER=1 \
    FLASK_APP=manage.py

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-local.txt requirements-analysis.txt api/requirements.txt /app/
COPY docker/python/requirements-docker.txt /app/requirements-docker.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements-docker.txt

COPY core/ /app/core/
COPY app/ /app/app/
COPY api/ /app/api/
COPY compute/ /app/compute/
COPY analysis/ /app/analysis/
COPY jobs/ /app/jobs/
COPY migrations/ /app/migrations/
COPY manage.py /app/manage.py
COPY bin/ /app/bin/

CMD ["python", "-m", "compute", "eod_all"]
