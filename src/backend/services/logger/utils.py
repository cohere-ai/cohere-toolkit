from fastapi import HTTPException, status

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
        level = Settings().logger.level
        renderer = Settings().logger.renderer

        if strategy == "structlog":
            return StructuredLogging(level, renderer)
        else:
            # Default to StructuredLogging
            return StructuredLogging(level, renderer)


def log_and_raise_http_exception(logger: BaseLogger, error_message: str):
    logger.error(event=error_message)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"{error_message}",
    )
