from celery import Celery

"""
Run celery as a listener

celery -A src.backend.services.sync worker -P gevent --loglevel=INFO

Run celery as a daemon
todo
"""

# Start celery.
app = Celery("toolkit_sync")
app.config_from_object("src.backend.services.sync.celeryconfig")
