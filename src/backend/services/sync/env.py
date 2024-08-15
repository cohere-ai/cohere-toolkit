from functools import lru_cache

from backend.services.sync.config import Configuration
from pydantic import ValidationError


@lru_cache(maxsize=1)
def env() -> Configuration:
    try:
        return Configuration()
    except ValidationError as e:
        Configuration.handle_validation_error(e)
