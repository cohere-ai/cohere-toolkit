# Celery configuration
# http://docs.celeryproject.org/en/latest/configuration.html
import ssl

from backend.config import env

config = env()

# broker and db
broker_url = config.REDIS_CONNECTION_STRING
broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE} if config.REDIS_USE_SSL else None

# see https://docs.celeryq.dev/en/stable/userguide/configuration.html#database-url-examples
result_backend = "db+{}".format(config.APOLLO_DB_CONNECTION_URL)

# extended tasks format
result_extended = True

# retry connecting if disconnected
broker_connection_retry_on_startup = True

# update task status when STARTED
task_track_started = True

# default task priority
task_default_priority = 5

# result format
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

# custom table names
database_table_names = {
    "task": "sync_celery_taskmeta",
    "group": "sync_celery_tasksetmeta",
}

# pool config
# For info on decision-making https://celery.school/celery-worker-pools#heading-threads
# The worker_pool setting shouldn't be used to select the eventlet/gevent
# pools, instead you *must use the -P* argument so that patches are applied
# as early as possible.
# worker_pool = "gevent"
worker_concurrency = config.APOLLO_EXECUTOR_CONCURRENCY

# regarding broker_pool_limit https://stackoverflow.com/a/68546019/11582081
# https://groups.google.com/g/celery-users/c/kjJb5-MhcZs/m/iNJEqNtkzuIJ
worker_prefetch_multiplier = 1

# Use UTC instead of localtime
CELERY_enable_utc = True

# modules to include
include = ["apollo.core.eval", "apollo.core.generate", "apollo.core.chat"]

# Send task events for Prometheus metrics
worker_send_task_events = True
task_send_sent_event = True
