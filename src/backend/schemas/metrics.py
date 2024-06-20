import time
import uuid
from typing import Any

from pydantic import BaseModel


class MetricsDataBase(BaseModel):
    id: str = str(uuid.uuid4())
    trace_id: str | None = None
    method: str
    endpoint_name: str
    success: bool
    user_id_hash: str | None = None
    timestamp: float = time.time()
    secret: str = "secret"
    duration: float | None = None


class MetricsData(MetricsDataBase):
    object_ids: dict[str, str] | None = None
    status_code: int | None = None
    input_nb_tokens: int | None = None
    output_nb_tokens: int | None = None
    search_units: int | None = None
    model: str | None = None
    error: str | None = None
    agent: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None
