from fastapi import Request

from backend.crud import user as user_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.user import User
from backend.schemas.agent import Agent, AgentToolMetadata
from backend.schemas.metrics import MetricsAgent, MetricsMessageType, MetricsUser
from backend.services.auth.utils import get_header_user_id

DEFAULT_METRICS_AGENT = MetricsAgent(
    id="9c300cfd-1506-408b-829d-a6464137a7c1",
    version="1",
    name="Default Agent",
    temperature=0.3,
    model="command-r-plus",
    deployment="Cohere",
    preamble="",
    description="default",
)


def add_event_type_to_request_state(request: Request, event_type: MetricsMessageType):
    request.state.event_type = event_type


def add_default_agent_to_request_state(request: Request):
    request.state.agent = DEFAULT_METRICS_AGENT


def add_agent_to_request_state(request: Request, agent: Agent):
    request.state.agent = MetricsAgent(
        id=agent.id,
        version=agent.version,
        name=agent.name,
        temperature=agent.temperature,
        model=agent.model,
        deployment=agent.deployment,
        preamble=agent.preamble,
        description=agent.description,
    )


def add_session_user_to_request_state(request: Request, session: DBSessionDep):
    user_id = get_header_user_id(request)
    if user_id:
        user = user_crud.get_user(session, user_id)
        if user:
            request.state.user = MetricsUser(
                id=user.id, email=user.email, fullname=user.fullname
            )


def add_user_to_request_state(request: Request, user: User):
    if user:
        request.state.user = MetricsUser(
            id=user.id, email=user.email, fullname=user.fullname
        )


def add_agent_tool_metadata_to_request_state(
    request: Request, agent_tool_metadata: AgentToolMetadata
):
    if agent_tool_metadata:
        request.state.agent_tool_metadata = agent_tool_metadata
