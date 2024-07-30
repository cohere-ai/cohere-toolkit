import logging
from typing import Any

from backend.config.settings import Settings
from backend.services.logger.strategies.structured_log import StructuredLogging


def get_logger():
    strategy = Settings().logger.strategy
    level_str = Settings().logger.level
    renderer = Settings().logger.renderer

    level = getattr(logging, level_str.upper(), None)

    if strategy == "structlog":
        return StructuredLogging(level, renderer)
    else:
        raise ValueError(f"Invalid logger strategy: {strategy}")
