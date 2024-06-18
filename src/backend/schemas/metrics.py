import time
import uuid

from pydantic import BaseModel


class MetricsDataBase(BaseModel):
    id: str = str(uuid.uuid4())
    # assistant_id: str
    trace_id: str
    method: str
    endpoint_name: str
    success: bool
    user_id_hash: str | None = None
    timestamp: float = time.time()
    secret: str = "secret"


class MetricsData(MetricsDataBase):
    object_ids: dict[str, str] | None = None
    status_code: int | None = None
    input_nb_tokens: int | None = None
    output_nb_tokens: int | None = None
    search_units: int | None = None
    model: str | None = None
    error: str | None = None
