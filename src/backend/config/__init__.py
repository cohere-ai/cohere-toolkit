from functools import lru_cache

from backend.config.settings import Settings


@lru_cache(maxsize=1)
def settings() -> Settings:
    return Settings()
