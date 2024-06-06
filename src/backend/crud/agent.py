from sqlalchemy.orm import Session

from backend.database_models.agent import Agent
from backend.schemas.agent import UpdateAgent


def create_agent(db: Session, agent: Agent) -> Agent:
    """
    Create a new agent.

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


def get_agent(db: Session, agent_id: str) -> Agent:
    """
    Get an agent by its ID.

    Args:
      db (Session): Database session.
      agent_id (str): Agent ID.

    Returns:
      Agent: Agent with the given ID.
    """
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_agents(db: Session, offset: int = 0, limit: int = 100) -> list[Agent]:
    """
    Get all agents for a user.

    Args:
      db (Session): Database session.
      offset (int): Offset of the results.
      limit (int): Limit of the results.

    Returns:
      list[Agent]: List of agents.
    """
    return db.query(Agent).offset(offset).limit(limit).all()


def update_agent(db: Session, agent: Agent, new_agent: UpdateAgent) -> Agent:
    """
    Update an agent.

    Args:
      db (Session): Database session.
      agent (Agent): Agent to be updated.
      new_agent (UpdateAgent): New agent.

    Returns:
      Agent: Updated agent.
    """
    for attr, value in new_agent.model_dump().items():
        setattr(agent, attr, value)
    db.commit()
    db.refresh(agent)
    return agent


def delete_agent(db: Session, agent_id: str) -> None:
    """
    Delete an agent by ID.

    Args:
        db (Session): Database session.
        agent_id (str): Agent ID.
    """
    agent = db.query(Agent).filter(Agent.id == agent_id)
    agent.delete()
    db.commit()
