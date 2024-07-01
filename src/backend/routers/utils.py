from fastapi import Request

from backend.crud import user as user_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.user import User
from backend.schemas.agent import Agent
from backend.schemas.metrics import MetricsAgent, MetricsUser
from backend.services.auth.utils import get_header_user_id


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
