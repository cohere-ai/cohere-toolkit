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

# TODO: get by org id instead of user id
def get_agent(db: Session, agent_id: str, user_id: str) -> Agent:
  """
  Get an agent by its ID.

  Args:
    db (Session): Database session.
    agent_id (str): Agent ID.
    user_id (str): User ID.

  Returns:
    Agent: Agent with the given ID.
  """
  return db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == user_id).first()

# TODO: get by org id instead of user id
def get_agents(db: Session, user_id: str, offset: int = 0, limit: int = 100) -> list[Agent]:
  """
  Get all agents for a user.

  Args:
    db (Session): Database session.
    user_id (str): User ID.
    offset (int): Offset of the results.
    limit (int): Limit of the results.

  Returns:
    list[Agent]: List of agents.
  """
  return (
      db.query(Agent)
      .filter(Agent.user_id == user_id)
      .offset(offset)
      .limit(limit)
      .all()
  )

# TODO: use org id instead of user id
def update_agents(db: Session, agent: Agent, new_agent: UpdateAgent) -> Agent:
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

# TODO: use org id instead of user id
def delete_agent(db: Session, agent_id: str, user_id: str) -> None:
    """
    Delete a message by ID.

    Args:
        db (Session): Database session.
        agent_id (str): Agent ID.
        user_id (str): User ID.
    """
    agent = db.query(Agent).filter(
        Agent.id == agent_id, Agent.user_id == user_id
    )
    agent.delete()
    db.commit()
