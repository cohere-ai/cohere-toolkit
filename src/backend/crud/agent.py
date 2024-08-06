from sqlalchemy.orm import Session

from backend.database_models import Deployment
from backend.database_models.agent import Agent, AgentDeploymentModel
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
def get_agent_by_id(db: Session, agent_id: str) -> Agent:
    """
    Get an agent by its ID.

    Args:
      db (Session): Database session.
      agent_id (str): Agent ID.

    Returns:
      Agent: Agent with the given ID.
    """
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_agent_by_name(db: Session, agent_name: str) -> Agent:
    """
    Get an agent by its name.

    Args:
      db (Session): Database session.
      agent_name (str): Agent name.

    Returns:
      Agent: Agent with the given name.
    """
    return db.query(Agent).filter(Agent.name == agent_name).first()


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


def get_agents(
    db: Session,
    offset: int = 0,
    limit: int = 100,
    organization_id: str = None,
    user_id: str = None,
) -> list[Agent]:
    """
    Get all agents for a user.

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

    if organization_id is not None:
        query = query.filter(Agent.organization_id == organization_id)
    if user_id is not None:
        query = query.filter(Agent.user_id == user_id)
    query = query.offset(offset).limit(limit)
    return query.all()


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
def update_agent(db: Session, agent: Agent, new_agent: UpdateAgentRequest) -> Agent:
    """
    Update an agent.

    Args:
      db (Session): Database session.
      agent (Agent): Agent to be updated.
      new_agent (UpdateAgentRequest): New agent.

    Returns:
      Agent: Updated agent.
    """
    for attr, value in new_agent.model_dump(exclude_none=True).items():
        setattr(agent, attr, value)

    db.commit()
    db.refresh(agent)
    return agent


@validate_transaction
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
    return None
