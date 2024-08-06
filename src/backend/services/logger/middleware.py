import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from backend.services.context import get_context


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_body = await request.body()
        start_time = time.time()

        response = await call_next(request)

        ctx = get_context(request)
        logger = ctx.get_logger()

        logger.info(
            event="Request",
            method=request.method,
            body=request_body,
            path=request.url.path,
            status_code=response.status_code,
            duration=time.time() - start_time,
            response=response,
            # ctx=ctx,
        )

        return response
