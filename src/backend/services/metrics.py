import os
import time
import uuid

import requests
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import Message

REPORT_ENDPOINT = os.getenv("REPORT_ENDPOINT", "")

import time

from starlette.responses import Response


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.trace_id = str(uuid.uuid4())
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        self.report_request_metrics(request.scope, response, duration, request)

        return response

    def report_request_metrics(self, scope, response, duration, request):
        trace_id = None
        if hasattr(request.state, "trace_id"):
            trace_id = request.state.trace_id

        if scope["type"] == "http":
            timestamp = time.time()
            data = {
                "trace_id": trace_id,
                "endpoint_name": self.get_endpoint_name(scope),
                "method": self.get_method(scope),
                "status_code": self.get_status_code(response),
                "timestamp": timestamp,
                "duration": duration,
            }

            report_metrics(data)

    def get_method(self, scope):
        try:
            return scope["method"]
        except KeyError:
            return "unknown"
        except Exception as e:
            print("Failed to get method:", e)
            return "unknown"

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


def report_metrics(data):
    if not REPORT_ENDPOINT:
        print("No report endpoint set")
        return

    try:
        data["id"] = str(uuid.uuid4())
        requests.post(REPORT_ENDPOINT, json=data)
    except Exception as e:
        print("Failed to report metrics:", e)
