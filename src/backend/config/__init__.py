from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import ValidationError

from backend.config.config import Configuration


@lru_cache(maxsize=1)
def env() -> Configuration:
    try:
        return Configuration()
    except ValidationError as e:
        Configuration.handle_validation_error(e)


ConfigDep = Annotated[Configuration, Depends(env)]
