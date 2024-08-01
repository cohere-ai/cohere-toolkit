import logging

from backend.config.settings import Settings
from backend.services.logger.strategies.base import BaseLogger
from backend.services.logger.strategies.structured_log import StructuredLogging


class LoggerFactory:
    def __init__(self):
        self.logger = None

    def get_logger(self) -> BaseLogger:
        if self.logger is not None:
            return self.logger

        strategy = Settings().logger.strategy
        level_str = Settings().logger.level
        renderer = Settings().logger.renderer

        level = getattr(logging, level_str.upper(), None)

        if strategy == "structlog":
            return StructuredLogging(level, renderer)
        else:
            # Default to StructuredLogging
            return StructuredLogging(level, renderer)


logger = LoggerFactory().get_logger()
