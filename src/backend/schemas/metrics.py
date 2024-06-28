import time
import uuid
from typing import Any

from pydantic import BaseModel


class MetricsDataBase(BaseModel):
    id: str
    user_id: str
    trace_id: str
    method: str
    endpoint_name: str
    success: bool
    timestamp: float = time.time()
    secret: str = ""


class MetricsUser(BaseModel):
    id: str
    fullname: str
    email: str | None


class MetricsAgent(BaseModel):
    id: str
    version: int
    name: str
    temperature: float
    model: str
    deployment: str | None
    preamble: str | None
    description: str | None


class MetricsData(MetricsDataBase):
    status_code: int | None = None
    input_nb_tokens: int | None = None
    output_nb_tokens: int | None = None
    search_units: int | None = None
    model: str | None = None
    error: str | None = None
    object_ids: dict[str, str] | None = None
    duration_ms: float | None = None
    meta: dict[str, Any] | None = None
    assistant_id: str | None = None
    assistant: MetricsAgent | None = None
    user: MetricsUser | None = None


class MetricsSignal(BaseModel):
    signal: MetricsData
