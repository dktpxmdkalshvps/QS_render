#!/usr/bin/env bash
set -o errexit
python --version
alembic upgrade head
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} --workers ${WEB_CONCURRENCY:-2} --timeout 120
