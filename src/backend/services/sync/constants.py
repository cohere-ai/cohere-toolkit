from enum import Enum

from dotenv import load_dotenv

from backend.config.settings import Settings

load_dotenv()

DEFAULT_TIME_OUT = 10 * 60
SYNC_BROKER_URL = Settings().sync.broker_url
SYNC_DATABASE_URL = Settings().database.url
SYNC_WORKER_CONCURRENCY = int(Settings().sync.worker_concurrency)


class Status(Enum):
    SUCCESS = "success"
    CANCELLED = "cancelled"
    FAIL = "fail"
