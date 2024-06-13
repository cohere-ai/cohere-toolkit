import asyncio
import os
import threading
import time
import uuid
from time import sleep

import httpx
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
        data = self.get_data(request.scope, response, duration, request)
        threading.Thread(target=run_in_new_thread, args=(data,)).start()
        return response

    def get_data(self, scope, response, duration, request):
        data = {}
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

        return data

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


async def report_metrics(data):
    if not REPORT_ENDPOINT:
        print("No report endpoint set")
        return

    try:
        data["id"] = str(uuid.uuid4())
        async with httpx.AsyncClient() as client:
            await client.post(REPORT_ENDPOINT, json=data)
    except Exception as e:
        print("Failed to report metrics:", e)


def run_in_new_thread(data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(report_metrics(data))
    loop.close()
