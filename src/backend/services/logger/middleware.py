import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from backend.services.context import get_context


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        ctx = get_context(request)
        logger = ctx.get_logger()

        logger.info(
            event="Request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=time.time() - start_time,
            ctx=ctx,
        )

        return response
