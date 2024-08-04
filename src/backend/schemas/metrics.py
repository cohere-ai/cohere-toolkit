from enum import Enum
from typing import Any

from pydantic import BaseModel

from backend.schemas.agent import Agent


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
    # implemented, has tests
    CHAT_API_SUCCESS = "chat_api_call_success"
    # implemented, needs tests
    CHAT_API_FAIL = "chat_api_call_failure"
    # implemented, has tests
    RERANK_API_SUCCESS = "rerank_api_call_success"
    # implemented, needs tests
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
    model: str | None
    deployment: str | None
    preamble: str | None
    description: str | None


class MetricsModelAttrs(BaseModel):
    input_nb_tokens: int
    output_nb_tokens: int
    search_units: int
    model: str
    assistant_id: str


class MetricsData(MetricsDataBase):
    input_nb_tokens: int | None = None
    output_nb_tokens: int | None = None
    search_units: int | None = None
    model: str | None = None
    error: str | None = None
    duration_ms: float | None = None
    meta: dict[str, Any] | None = None
    assistant_id: str | None = None
    assistant: MetricsAgent | None = None
    user: MetricsUser | None = None


class MetricsSignal(BaseModel):
    signal: MetricsData


DEFAULT_METRICS_AGENT = MetricsAgent(
    id="9c300cfd-1506-408b-829d-a6464137a7c1",
    version=1,
    name="Default Agent",
    temperature=0.3,
    model="command-r-plus",
    deployment="Cohere",
    preamble="",
    description="default",
)


def agent_to_metrics_agent(agent: Agent | None) -> MetricsAgent:
    if not agent:
        return None
    # TODO Eugene: Check agent.model and agent.deployment after the refactor Agent deployment
    #  and model to object(if needed)
    return MetricsAgent(
        id=agent.id,
        version=agent.version,
        name=agent.name,
        temperature=agent.temperature,
        model=agent.model if agent.model else None,
        deployment=agent.deployment if agent.deployment else None,
        preamble=agent.preamble,
        description=agent.description,
    )
