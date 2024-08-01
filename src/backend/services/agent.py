from typing import Optional

from fastapi import HTTPException

from backend.crud import agent as agent_crud
from backend.crud import agent_tool_metadata as agent_tool_metadata_crud
from backend.database_models.agent import Agent, AgentToolMetadata
from backend.database_models.database import DBSessionDep


def validate_agent_exists(session: DBSessionDep, agent_id: str) -> Agent:
    agent = agent_crud.get_agent_by_id(session, agent_id)

    if not agent:
        raise HTTPException(
            status_code=400,
            detail=f"Agent with ID {agent_id} not found.",
        )

    return agent


def validate_agent_tool_metadata_exists(
    session: DBSessionDep, agent_tool_metadata_id: str
) -> AgentToolMetadata:
    agent_tool_metadata = agent_tool_metadata_crud.get_agent_tool_metadata_by_id(
        session, agent_tool_metadata_id
    )

    if not agent_tool_metadata:
        raise HTTPException(
            status_code=400,
            detail=f"Agent tool metadata with ID {agent_tool_metadata_id} not found.",
        )

    return agent_tool_metadata


def raise_db_error(e: Exception, type: str, name: str):
    if "psycopg2.errors.UniqueViolation" in str(e):
        raise HTTPException(
            status_code=400,
            detail=f"{type} {name} already exists for given user and agent.",
        )

    raise HTTPException(status_code=500, detail=str(e))


def get_public_and_private_agents(
    session: DBSessionDep,
    user_id: str,
    organization_id: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
) -> list[Agent]:
    public_agents = agent_crud.get_public_agents(
        session, organization_id=organization_id, offset=offset, limit=limit
    )
    private_agents = agent_crud.get_private_agents(
        session, user_id=user_id, offset=offset, limit=limit
    )

    return public_agents + private_agents


def validate_user_has_access_to_agent(user_id: str, agent: Agent | None) -> bool:
    # Check if agent exists and user has access to it
    error = None
    if not agent:
        error = "Agent not found."

    if agent and agent.user_id != user_id and not agent.is_private:
        error = f"Agent with ID: {agent.id} not found."

    if error:
        raise HTTPException(status_code=404, detail=error)

    return True
