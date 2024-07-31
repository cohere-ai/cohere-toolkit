import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from backend.services.context import get_context
from backend.services.logger.utils import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)

        ctx = get_context(request)

        # Bind context to logger
        logger.bind(
            user_id=ctx.get_user_id(),
            trace_id=ctx.get_trace_id(),
            ctx=ctx,
        )

        logger.info(
            event="Request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=time.time() - start_time,
            ctx=ctx,
        )

        return response
