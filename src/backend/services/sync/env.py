from functools import lru_cache

from pydantic import ValidationError

from backend.services.sync.config import Configuration


@lru_cache(maxsize=1)
def env() -> Configuration:
    try:
        return Configuration()
    except ValidationError as e:
        Configuration.handle_validation_error(e)
