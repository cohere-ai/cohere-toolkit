import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)

        logging.info(f"{request.method} {request.url.path}\n{request.headers}")
        return response


def get_logger():
    """
    Get the logger for the service

    Returns:
        logger: The logger for the service
    """
    # get logger and configure it
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger(__name__)

    return logger


def send_log_message(
    logger: logging.Logger, message: str, level: str = "info", **kwargs
):
    """
    Send a log message to the logger
    Args:
        logger (logging.Logger): The logger to send the message to.
        message (str): The message to send.
        level (str): The level of the message. Valid levels are "debug", "info", "warning", "error", and "critical".
        **kwargs: Additional keyword arguments passed to the logging function.
    Raises:
        ValueError: If an invalid log level is provided.
    """
    log_levels = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
        "critical": logger.critical,
    }

    log_func = log_levels.get(level)

    if not log_func:
        raise ValueError(f"Invalid log level: {level}")

    log_details = {
        "message": message,
        **kwargs,
    }

    log_func(log_details)
