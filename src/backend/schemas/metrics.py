import time
import uuid
from typing import Any

from pydantic import BaseModel


class MetricsDataBase(BaseModel):
    id: str = str(uuid.uuid4())
    trace_id: str
    method: str
    endpoint_name: str
    success: bool
    timestamp: float = time.time()
    secret: str = "secret"


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
    assistant: dict[str, Any] | None = None
    user_id: str
    user: dict[str, Any] | None = None


class MetricsSignal(BaseModel):
    signal: MetricsData
