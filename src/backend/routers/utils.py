from fastapi import Request

from backend.crud import agent as agent_crud
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


def add_model_to_request_state(request: Request, model: str):
    request.state.model = model


def add_default_agent_to_request_state(request: Request):
    # default_agent = agent_crud.get_agent_by_id("default")
    # if default_agent:
    #     add_agent_to_request_state(request, default_agent)
    # else:
    request.state.agent = DEFAULT_METRICS_AGENT


def add_agent_to_request_state(request: Request, agent: Agent):
    request.state.agent = MetricsAgent(
        id=agent.id,
        version=agent.version,
        name=agent.name,
        temperature=agent.temperature,
        model=str(agent.model),
        deployment=str(agent.deployment),
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


def get_deployment_model_from_agent(agent: Agent, session: DBSessionDep):
    from backend.crud import deployment as deployment_crud

    model_db = None
    deployment_db = deployment_crud.get_deployment_by_name(session, agent.deployment)
    if not deployment_db:
        deployment_db = deployment_crud.get_deployment(session, agent.deployment)
    if deployment_db:
        model_db = next(
            (
                model
                for model in deployment_db.models
                if model.name == agent.model or model.id == agent.model
            ),
            None,
        )
    return deployment_db, model_db


def get_tools_from_agent(agent: Agent, session: DBSessionDep):
    from backend.crud import tool as tool_crud

    tools_db = tool_crud.get_available_tools(session)
    tools = []
    for tool in tools_db:
        if tool.name in agent.tools:
            tools.append(tool)
    return tools
