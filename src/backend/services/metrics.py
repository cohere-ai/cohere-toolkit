import os
import time

import requests
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

REPORT_ENDPOINT = os.getenv("REPORT_ENDPOINT", "")


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)

        duration = time.time() - start_time

        if REPORT_ENDPOINT:
            await self.report_metrics(request.scope, response, duration)

        return response

    async def report_metrics(self, scope, response, duration):
        if scope["type"] == "http":
            timestamp = time.time()
            data = {
                "endpoint_name": self.get_endpoint_name(scope),
                "status_code": self.get_status_code(response),
                "timestamp": timestamp,
                "duration": duration,
            }

            try:
                requests.post(REPORT_ENDPOINT, json=data)
            except Exception as e:
                print("Failed to report metrics:", e)

    def get_endpoint_name(self, scope):
        try:
            return scope["path"]
        except KeyError:
            return "unknown"
        except Exception as e:
            print("Failed to get endpoint name:", e)
            return "unknown"

    def get_status_code(self, response):
        try:
            return response.status_code
        except Exception as e:
            print("Failed to get status code:", e)
            return 500
