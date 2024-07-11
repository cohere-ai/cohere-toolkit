from sqlalchemy.orm import Session

from backend.database_models.agent import Agent
from backend.schemas.agent import UpdateAgentRequest


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
    try:
        db.add(agent)
        db.commit()
        db.refresh(agent)
    except Exception as e:
        db.rollback()
        raise e

    return agent


def get_agent_by_id(db: Session, agent_id: str) -> Agent:
    """
    Get an agent by its ID.

    Args:
      db (Session): Database session.
      agent_id (str): Agent ID.

    Returns:
      Agent: Agent with the given ID.
    """
    agent = None

    try:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
    except Exception as e:
        db.rollback()
        raise e

    return agent


def get_agent_by_name(db: Session, agent_name: str) -> Agent:
    """
    Get an agent by its name.

    Args:
      db (Session): Database session.
      agent_name (str): Agent name.

    Returns:
      Agent: Agent with the given name.
    """
    agent = None

    try:
        agent = db.query(Agent).filter(Agent.name == agent_name).first()
    except Exception as e:
        db.rollback()
        raise e

    return agent


def get_agents(
    db: Session,
    offset: int = 0,
    limit: int = 100,
    organization_id: str = None,
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
    agents = None

    try:
        query = db.query(Agent)
        if organization_id is not None:
            query = query.filter(Agent.organization_id == organization_id)
        query = query.offset(offset).limit(limit)
        agents = query.all()
    except Exception as e:
        db.rollback()
        raise e

    return agents


def update_agent(db: Session, agent: Agent, new_agent: UpdateAgentRequest) -> Agent:
    """
    Update an agent.

    Args:
      db (Session): Database session.
      agent (Agent): Agent to be updated.
      new_agent (UpdateAgent): New agent.

    Returns:
      Agent: Updated agent.
    """
    try:
        for attr, value in new_agent.model_dump(exclude_none=True).items():
            setattr(agent, attr, value)
        db.commit()
        db.refresh(agent)
    except Exception as e:
        db.rollback()
        raise e

    return agent


def delete_agent(db: Session, agent_id: str) -> None:
    """
    Delete an agent by ID.

    Args:
        db (Session): Database session.
        agent_id (str): Agent ID.
    """
    try:
        agent = db.query(Agent).filter(Agent.id == agent_id)
        agent.delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
