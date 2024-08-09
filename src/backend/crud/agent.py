from typing import Optional

from sqlalchemy.orm import Session

from backend.database_models import Deployment
from backend.database_models.agent import Agent, AgentDeploymentModel
from backend.schemas.agent import AgentVisibility, UpdateAgentRequest
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


@validate_transaction
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


@validate_transaction
def get_association_by_deployment_name(
    db: Session, agent: Agent, deployment_name: str
) -> AgentDeploymentModel:
    """
    Get an agent deployment model association by deployment name.

    Args:
      db (Session): Database session.
      agent (Agent): Agent to get the association.
      deployment_name (str): Deployment name.

    Returns:
      AgentDeploymentModel: Agent deployment model association.
    """
    return (
        db.query(AgentDeploymentModel)
        .join(Deployment, Deployment.id == AgentDeploymentModel.deployment_id)
        .filter(
            Deployment.name == deployment_name,
            AgentDeploymentModel.agent_id == agent.id,
        )
        .first()
    )


@validate_transaction
def get_association_by_deployment_id(
    db: Session, agent: Agent, deployment_id: str
) -> AgentDeploymentModel:
    """
    Get an agent deployment model association by deployment id.

    Args:
      db (Session): Database session.
      agent (Agent): Agent to get the association.
      deployment_id (str): Deployment ID.

    Returns:
      AgentDeploymentModel: Agent deployment model association.
    """
    return (
        db.query(AgentDeploymentModel)
        .filter(
            AgentDeploymentModel.deployment_id == deployment_id,
            AgentDeploymentModel.agent_id == agent.id,
            AgentDeploymentModel.is_default_deployment == True,
            AgentDeploymentModel.is_default_model == True,
        )
        .first()
    )


@validate_transaction
def get_agents(
    db: Session,
    user_id: str,
    offset: int = 0,
    limit: int = 100,
    organization_id: Optional[str] = None,
    visibility: AgentVisibility = AgentVisibility.ALL,
) -> list[Agent]:
    """
    Get all agents for a user.
    Public agents are visible to everyone, private agents are only visible to the owner.

    Args:
        db (Session): Database session.
        offset (int): Offset of the results.
        limit (int): Limit of the results.
        organization_id (str): Organization ID.
        user_id (str): User ID.

    Returns:
      list[Agent]: List of agents.
    """
    query = db.query(Agent)

    # Filter by visibility
    if visibility == AgentVisibility.PUBLIC:
        query = query.filter(Agent.is_private == False)
    elif visibility == AgentVisibility.PRIVATE:
        query = query.filter(Agent.is_private == True, Agent.user_id == user_id)
    else:
        query = query.filter((Agent.is_private == False) | (Agent.user_id == user_id))

    # Filter by organization and user
    if organization_id is not None:
        query = query.filter(Agent.organization_id == organization_id)

    query = query.offset(offset).limit(limit)
    return query.all()


@validate_transaction
def get_agent_model_deployment_association(
    db: Session, agent: Agent, model_id: str, deployment_id: str
) -> AgentDeploymentModel:
    """
    Get an agent model deployment association.

    Args:
      db (Session): Database session.
      agent (Agent): Agent to get the association.
      model_id (str): Model ID.
      deployment_id (str): Deployment ID.

    Returns:
      AgentDeploymentModel: Agent model deployment association.
    """
    return (
        db.query(AgentDeploymentModel)
        .filter(
            AgentDeploymentModel.agent_id == agent.id,
            AgentDeploymentModel.model_id == model_id,
            AgentDeploymentModel.deployment_id == deployment_id,
        )
        .first()
    )


@validate_transaction
def delete_agent_model_deployment_association(
    db: Session, agent: Agent, model_id: str, deployment_id: str
):
    """
    Delete an agent model deployment association.

    Args:
      db (Session): Database session.
      agent (Agent): Agent to delete the association.
      model_id (str): Model ID.
      deployment_id (str): Deployment ID.
    """
    db.query(AgentDeploymentModel).filter(
        AgentDeploymentModel.agent_id == agent.id,
        AgentDeploymentModel.model_id == model_id,
        AgentDeploymentModel.deployment_id == deployment_id,
    ).delete()
    db.commit()


@validate_transaction
def assign_model_deployment_to_agent(
    db: Session,
    agent: Agent,
    model_id: str,
    deployment_id: str,
    deployment_config: dict[str, str] = {},
    set_default: bool = False,
) -> Agent:
    """
    Assign a model and deployment to an agent.

    Args:
      agent (Agent): Agent to assign the model and deployment.
      model_id (str): Model ID.
      deployment_id (str): Deployment ID.
      deployment_config (dict[str, str]): Deployment configuration.
      set_default (bool): Set the model and deployment as default.

    Returns:
      Agent: Agent with the assigned model and deployment.
    """
    agent_deployment = AgentDeploymentModel(
        agent_id=agent.id,
        model_id=model_id,
        deployment_id=deployment_id,
        is_default_deployment=set_default,
        is_default_model=set_default,
        deployment_config=deployment_config,
    )
    db.add(agent_deployment)
    db.commit()
    db.refresh(agent)
    return agent


@validate_transaction
def update_agent(
    db: Session, agent: Agent, new_agent: UpdateAgentRequest, user_id: str
) -> Agent:
    """
    Update an agent.

    Args:
      db (Session): Database session.
      agent (Agent): Agent to be updated.
      new_agent (UpdateAgentRequest): New agent.

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


@validate_transaction
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
