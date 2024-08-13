#!/bin/sh

cd /app
export PYTHONPATH="$PYTHONPATH:/app/src"
/app/.venv/bin/python3 src/backend/services/sync/publish.py