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
