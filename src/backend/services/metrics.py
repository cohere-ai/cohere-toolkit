import asyncio
import hashlib
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
                "method": self.get_method(scope),
                "endpoint_name": self.get_endpoint_name(scope),
                "user_id_hash": self.get_user_id_hash(request),
                "success": self.get_success(response),
                "trace_id": trace_id,
                "timestamp": timestamp,
                "duration": duration,
                "status_code": self.get_status_code(response),
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

    def get_success(self, response):
        try:
            return 200 <= response.status_code < 400
        except Exception as e:
            print("Failed to get success:", e)
            return False

    def get_user_id_hash(self, request):
        try:
            user_id = request.headers.get("User-Id", None)
            return hash_string(user_id)
        except Exception as e:
            print("Failed to get user id hash:", e)
            return None


def hash_string(s):
    if s is None:
        return None

    return hashlib.sha256(s.encode()).hexdigest()


async def report_metrics(data):
    data["id"] = str(uuid.uuid4())

    if not REPORT_ENDPOINT:
        print("No report endpoint set")
        return

    try:
        async with httpx.AsyncClient() as client:
            await client.post(REPORT_ENDPOINT, json=data)
    except Exception as e:
        print("Failed to report metrics:", e)


def run_in_new_thread(data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(report_metrics(data))
    loop.close()
