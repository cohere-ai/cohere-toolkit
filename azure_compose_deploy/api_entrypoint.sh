#!/bin/bash

poetry run alembic -c src/backend/alembic.ini upgrade head
exec uvicorn backend.main:app --workers=4 --host 0.0.0.0 --port ${PORT} --timeout-keep-alive 300
