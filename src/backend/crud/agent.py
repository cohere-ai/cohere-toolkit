from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import false, true

from backend.database_models.agent import Agent
from backend.schemas.agent import AgentVisibility, UpdateAgentDB
from backend.services.transaction import validate_transaction


@validate_transaction
def create_agent(db: Session, agent: Agent) -> Agent:
    """
    Create a new agent.

    Agents are configurable entities that can be specified to use specific tools and have specific preambles for better task completion.

    Args:
      db (Session): Database session.
      agent (Agent): Agent to be created.

    Returns:
      Agent: Created agent.
    """
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@validate_transaction
def get_agent_by_id(
    db: Session, agent_id: str, user_id: str = "", override_user_id: bool = False
) -> Agent:
    """
    Get an agent by its ID.
    Anyone can get a public agent, but only the owner can get a private agent.

    Args:
      db (Session): Database session.
      agent_id (str): Agent ID.
      user_id (str): User ID.
      override_user_id (bool): Override user ID check. Should only be used for internal operations.

    Returns:
      Agent: Agent with the given ID.
    """
    if override_user_id:
        return db.query(Agent).filter(Agent.id == agent_id).first()

    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    # Cannot GET privates Agents not belonging to you
    if agent and agent.is_private and agent.user_id != user_id:
        return None

    return agent


@validate_transaction
def get_agent_by_name(db: Session, agent_name: str, user_id: str) -> Agent:
    """
    Get an agent by its name.
    Anyone can get a public agent, but only the owner can get a private agent.

    Args:
      db (Session): Database session.
      agent_name (str): Agent name.
      user_id (str): User ID.

    Returns:
      Agent: Agent with the given name.
    """
    agent = db.query(Agent).filter(Agent.name == agent_name).first()

    if agent and agent.is_private and agent.user_id != user_id:
        return None

    return agent


@validate_transaction
def get_agents(
    db: Session,
    user_id: str = "",
    offset: int = 0,
    limit: int = 100,
    organization_id: Optional[str] = None,
    visibility: AgentVisibility = AgentVisibility.ALL,
    override_user_id: bool = False,
) -> list[Agent]:
    """
    Get all agents for a user.
    Public agents are visible to everyone, private agents are only visible to the owner.

    Args:
        db (Session): Database session.
        user_id (str): User ID.
        offset (int): Offset of the results.
        limit (int): Limit of the results.
        organization_id (str): Organization ID.
        visibility (AgentVisibility): Visibility of the agents.
        override_user_id (bool): Override user ID check. Should only be used for internal operations.

    Returns:
      list[Agent]: List of agents.
    """
    query = db.query(Agent)
    if override_user_id:
        return query.all()

    # Filter by visibility
    if visibility == AgentVisibility.PUBLIC:
        query = query.filter(Agent.is_private == false())
    elif visibility == AgentVisibility.PRIVATE:
        query = query.filter(Agent.is_private == true(), Agent.user_id == user_id)
    else:
        query = query.filter((Agent.is_private == false()) | (Agent.user_id == user_id))

    # Filter by organization and user
    if organization_id is not None:
        query = query.filter(Agent.organization_id == organization_id)

    query = query.offset(offset).limit(limit)
    return query.all()


@validate_transaction
def update_agent(
    db: Session, agent: Agent, new_agent: UpdateAgentDB, user_id: str
) -> Agent:
    """
    Update an agent.

    Args:
      db (Session): Database session.
      agent (Agent): Agent to be updated.
      new_agent (UpdateAgentRequest): New agent.
      user_id (str): User ID.

    Returns:
      Agent: Updated agent.
    """
    if agent.is_private and agent.user_id != user_id:
        return None

    new_agent_cleaned = new_agent.model_dump(exclude_unset=True, exclude_none=True)

    for attr, value in new_agent_cleaned.items():
        setattr(agent, attr, value)

    db.commit()
    db.refresh(agent)
    return agent


@validate_transaction
def delete_agent(db: Session, agent_id: str, user_id: str) -> bool:
    """
    Delete an Agent by ID if the Agent was created by the user_id given.

    Args:
        db (Session): Database session.
        agent_id (str): Agent ID.
        user_id (str): User ID.

    Returns:
      bool: True if the Agent was deleted, False otherwise
    """
    agent_query = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user_id)
    agent = agent_query.first()

    if not agent:
        return False

    agent_query.delete()
    db.commit()
    return True
