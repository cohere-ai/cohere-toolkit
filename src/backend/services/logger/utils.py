import logging

from backend.config.settings import Settings
from backend.services.logger.strategies.structured_log import StructuredLogging


def get_logger():
    strategy = Settings().logger.strategy
    level_str = Settings().logger.level

    level = getattr(logging, level_str.upper(), None)

    if strategy == "structlog":
        return StructuredLogging(level)
    else:
        raise ValueError(f"Invalid logger strategy: {strategy}")
