from backend.config.settings import Settings
from backend.services.logger.strategies.base import BaseLogger
from backend.services.logger.strategies.structured_log import StructuredLogging


class LoggerFactory:
    def __init__(self):
        self.logger = None

    def get_logger(self) -> BaseLogger:
        if self.logger is not None:
            return self.logger

        strategy = Settings().get('logger.strategy')
        level = Settings().get('logger.level')
        renderer = Settings().get('logger.renderer')

        if strategy == "structlog":
            return StructuredLogging(level, renderer)
        else:
            # Default to StructuredLogging
            return StructuredLogging(level, renderer)
