#!/usr/bin/env bash

# Default to the production version.
if [ "$1" = "development" ]; then
  exec watchmedo auto-restart \
    --directory=src/backend --pattern=*.py --recursive -- \
    celery -A backend.services.sync worker -P gevent --loglevel=INFO
else
  exec celery -A backend.services.sync worker -P gevent --loglevel=INFO
fi
