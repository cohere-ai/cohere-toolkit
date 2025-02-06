import csv
import os
import time
from typing import Any, Dict, List

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

MONITORED_PATHS = ["/v1/conversations", "/v1/chat-stream"]

class RequestMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(prefix) for prefix in MONITORED_PATHS):
            start_time = time.time()
            response = await call_next(request)
            latency = time.time() - start_time
            collector.add_metric("request", request.url.path, latency)
        else:
            response = await call_next(request)

        return response



class MetricsCollector:
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []

    def add_metric(
            self,
            metric_type: str,
            name: str,
            latency: float,
            class_name: str = "",
            method_name: str = "",
            method_params: Dict[str, Any] = {},
            timestamp: float = time.time()
    ):
        self.metrics.append({
            "timestamp": timestamp or time.time(),
            "type": metric_type,
            "name": name,
            "class_name": class_name,
            "method_name": method_name,
            "method_params": method_params,
            "latency": latency
        })
        self.save_to_csv()

    def save_to_csv(self, filename: str = "./metrics/metrics.csv"):
        if not self.metrics:
            return
        keys = self.metrics[0].keys()
        file_exists = os.path.isfile(filename)
        with open(filename, mode='a' if file_exists else 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            if not file_exists:
                writer.writeheader()
            writer.writerows(self.metrics)
        self.metrics.clear()  # Clear after saving


# Singleton instance
collector = MetricsCollector()
