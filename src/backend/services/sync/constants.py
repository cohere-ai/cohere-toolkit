import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_TIME_OUT = 6 * 60
SYNC_BROKER_URL = os.getenv("BROKER_URL")
SYNC_DATABASE_URL = os.getenv("DATABASE_URL")
SYNC_WORKER_CONCURRENCY = int(os.getenv("SYNC_WORKER_CONCURRENCY"))
