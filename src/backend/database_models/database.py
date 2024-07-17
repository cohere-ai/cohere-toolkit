import threading
from functools import lru_cache

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker


class Database:
    lock = threading.Lock()

    def __init__(self, connection_url: sa.URL):
        self._engine: sa.Engine = sa.create_engine(
            connection_url, pool_size=5, max_overflow=10, pool_timeout=30
        )
        self._session = sessionmaker(bind=self._engine, expire_on_commit=False)

    @staticmethod
    def create(connection_url: sa.URL, run_migrations: bool = True):
        with Database.lock:
            return Database._singleton(connection_url, run_migrations)

    @staticmethod
    @lru_cache
    def _singleton(connection_url: sa.URL, run_migrations: bool = True):
        return Database(connection_url, run_migrations)

    def session(self):
        return self._session()
