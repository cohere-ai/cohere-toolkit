import time
import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel


class GenericResponseMessage(BaseModel):
    message: str


class MetricsMessageType(str, Enum):
    # users: implemented, has tests
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    # agents: implemented, has tests
    ASSISTANT_CREATED = "assistant_created"
    ASSISTANT_UPDATED = "assistant_updated"
    ASSISTANT_DELETED = "assistant_deleted"
    ASSISTANT_ACCESSED = "assistant_accessed"
    # chat: implemented
    CHAT_API_SUCCESS = "chat_api_call_success"
    CHAT_API_FAIL = "chat_api_call_failure"
    # rerank: implemented
    RERANK_API_SUCCESS = "rerank_api_call_success"
    RERANK_API_FAIL = "rerank_api_call_failure"
    # pending implementation
    ENV_LIVENESS = "env_liveness"
    COMPASS_NEW_INDEX = "compass_new_index"
    COMPASS_REMOVE_INDEX = "compass_remove_index"
    COMPASS_NEW_USER = "compass_new_user"
    COMPASS_REMOVE_USER = "compass_remove_user"
    UNKNOWN_SIGNAL = "unknown"


class MetricsDataBase(BaseModel):
    id: str
    user_id: str
    trace_id: str
    message_type: MetricsMessageType
    timestamp: float
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
    success: bool = False
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
