from logging import Logger
from typing import ClassVar

import httpx
from dotenv import load_dotenv

from backend.services.compass import Compass
from backend.services.logger import get_logger

load_dotenv()


class Configuration:
    # TODO: Env vars checking needs to happen here
    # model_config = SettingsConfigDict(env_file=".env", extra="allow", env_nested_delimiter=".", validate_default=True)
    logger: ClassVar[Logger] = get_logger()

    # TODO: Env vars checking needs to happen here
    # Skipping for now for simplicity
    COMPASS: Compass = Compass()

    httpx_client: httpx.Client = httpx.Client(http2=True, timeout=300)
