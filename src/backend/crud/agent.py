from sqlalchemy.orm import Session

from backend.database_models.agent import Agent
from backend.schemas.agent import UpdateAgentRequest
from backend.services.transaction import validate_transaction


@validate_transaction
def create_agent(db: Session, agent: Agent) -> Agent:
    """
    Create a new agent.

    Agents are configurable entities that can be specified to use specfic tools and have specific preambles for better task completion.

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
def get_agent_by_id(db: Session, agent_id: str, user_id: str) -> Agent:
    """
    Get an agent by its ID.
    Anyone can get a public agent, but only the owner can get a private agent.

    Args:
      db (Session): Database session.
      agent_id (str): Agent ID.

    Returns:
      Agent: Agent with the given ID.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if agent and agent.is_private and agent.user_id != user_id:
        return None
    return agent


def get_agent_by_name(db: Session, agent_name: str, user_id: str) -> Agent:
    """
    Get an agent by its name.
    Anyone can get a public agent, but only the owner can get a private agent.

    Args:
      db (Session): Database session.
      agent_name (str): Agent name.

    Returns:
      Agent: Agent with the given name.
    """
    agent = db.query(Agent).filter(Agent.name == agent_name).first()
    if agent and agent.is_private and agent.user_id != user_id:
        return None
    return agent


def get_public_agents(
    db: Session,
    offset: int = 0,
    limit: int = 100,
    organization_id: str = None,
) -> list[Agent]:
    """
    Get all agents that are public.

    Args:
      db (Session): Database session.
      offset (int): Offset of the results.
      limit (int): Limit of the results.
      organization_id (str): Organization ID.

    Returns:
      list[Agent]: List of agents.
    """
    query = db.query(Agent)

    # Public agents -> is_private = False or None
    query = query.filter((Agent.is_private == False) | (Agent.is_private == None))

    if organization_id is not None:
        query = query.filter(Agent.organization_id == organization_id)

    query = query.offset(offset).limit(limit)
    return query.all()


def get_private_agents(
    db: Session,
    user_id: str,
    offset: int = 0,
    limit: int = 100,
) -> list[Agent]:
    """
    Get all agents for a user.

    Args:
      db (Session): Database session.
      offset (int): Offset of the results.
      limit (int): Limit of the results.
      organization_id (str): Organization ID.

    Returns:
      list[Agent]: List of agents.
    """
    query = (
        db.query(Agent)
        .filter(Agent.user_id == user_id, Agent.is_private)
        .offset(offset)
        .limit(limit)
    )
    return query.all()


def update_agent(
    db: Session, agent: Agent, new_agent: UpdateAgentRequest, user_id: str
) -> Agent:
    """
    Update an agent.
    Anyone can update a public agent, but only the owner can update a private agent.

    Args:
      db (Session): Database session.
      agent (Agent): Agent to be updated.
      new_agent (UpdateAgent): New agent.

    Returns:
      Agent: Updated agent.
    """
    if agent.is_private and agent.user_id != user_id:
        return None

    for attr, value in new_agent.model_dump(exclude_none=True).items():
        setattr(agent, attr, value)

    db.commit()
    db.refresh(agent)
    return agent


def delete_agent(db: Session, agent_id: str, user_id: str) -> bool:
    """
    Delete an agent by ID.
    Anyone can delete a public agent, but only the owner can delete a private agent.

    Args:
        db (Session): Database session.
        agent_id (str): Agent ID.

    Returns:
        bool: True if the agent was deleted, False otherwise
    """
    agent_query = db.query(Agent).filter(Agent.id == agent_id)
    agent = agent_query.first()

    if not agent:
        return False

    if agent and agent.is_private and agent.user_id != user_id:
        return False

    agent_query.delete()
    db.commit()
    return True
