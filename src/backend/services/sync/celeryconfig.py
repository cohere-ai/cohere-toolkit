# Celery configuration
# http://docs.celeryproject.org/en/latest/configuration.html

import socket

from backend.services.sync.constants import (
    DEFAULT_TIME_OUT,
    SYNC_BROKER_URL,
    SYNC_DATABASE_URL,
    SYNC_WORKER_CONCURRENCY,
)

# Sockets timeout
# This helps with GDrive SDK download timeouts
socket.setdefaulttimeout(DEFAULT_TIME_OUT)

# Priorities.
# Celery implicitly shards into 4 queues, use that.
# https://docs.celeryq.dev/en/stable/userguide/routing.html#redis-message-priorities
#  0. Priority
#  1. Normal (default)
#  2. Slow
#  3. Background
task_default_priority = 1
broker_transport_options = {
    "priority_steps": list(range(4)),
    "sep": ":",
    "queue_order_strategy": "priority",
}

# broker and db
broker_url = SYNC_BROKER_URL

# see https://docs.celeryq.dev/en/stable/userguide/configuration.html#database-url-examples
result_backend = "db+{}".format(SYNC_DATABASE_URL)

# retry connecting if disconnected
broker_connection_retry_on_startup = True

# extended tasks format
result_extended = True

# retry connecting if disconnected
broker_connection_retry_on_startup = True

# update task status when STARTED
task_track_started = True

# How many messages to prefetch at a time multiplied by the number of concurrent processes
worker_prefetch_multiplier = 1

# If True, then the backend object is shared across threads
# result_backend_thread_safe = True

# The maximum number of connections that can be open in the connection pool
broker_pool_limit = SYNC_WORKER_CONCURRENCY

# Use UTC instead of localtime
CELERY_enable_utc = True

# result format
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

# custom table names
database_table_names = {
    "task": "sync_celery_taskmeta",
    "group": "sync_celery_tasksetmeta",
}

worker_concurrency = SYNC_WORKER_CONCURRENCY

# Use UTC instead of localtime
CELERY_enable_utc = True

# modules to include
include = [
    "backend.tools.google_drive",
]

# Send task events for Prometheus metrics
worker_send_task_events = True
task_send_sent_event = True
