from sqlalchemy.orm import Session

from backend.database_models.agent_tool_metadata import AgentToolMetadata
from backend.schemas.agent import UpdateAgentToolMetadataRequest


def create_agent_tool_metadata(
    db: Session, agent_tool_metadata: AgentToolMetadata
) -> AgentToolMetadata:
    """
    Create a new agent tool metadata.

    Args:
        db (Session): Database session.
        agent_tool_metadata (AgentToolMetadata): Agent tool metadata data to be created.

    Returns:
        AgentToolMetadata: Created agent tool metadata.
    """
    db.add(agent_tool_metadata)
    db.commit()
    db.refresh(agent_tool_metadata)
    return agent_tool_metadata


def get_agent_tool_metadata_by_id(
    db: Session, agent_tool_metadata_id: str
) -> AgentToolMetadata:
    """
    Get a agent tool metadata by its ID.

    Args:
        db (Session): Database session.
        agent_tool_metadata_id (str): Agent tool metadata ID.

    Returns:
        AgentToolMetadata: Agent tool metadata with the given ID.
    """
    return (
        db.query(AgentToolMetadata)
        .filter(AgentToolMetadata.id == agent_tool_metadata_id)
        .first()
    )


def get_all_agent_tool_metadata_by_agent_id(
    db: Session, agent_id: str
) -> list[AgentToolMetadata]:
    """
    Get a agent tool metadata by its agent ID.

    Args:
        db (Session): Database session.
        agent_id (str): Agent ID.

    Returns:
        list[AgentToolMetadata]: List of agent tool metadata with the given agent ID.
    """
    return (
        db.query(AgentToolMetadata).filter(AgentToolMetadata.agent_id == agent_id).all()
    )


def update_agent_tool_metadata(
    db: Session,
    agent_tool_metadata: AgentToolMetadata,
    new_agent_tool_metadata: UpdateAgentToolMetadataRequest,
) -> AgentToolMetadata:
    """
    Update a agent tool metadata.

    Args:
        db (Session): Database session.
        agent_tool_metadata (AgentToolMetadata): Agent tool metadata to be updated.
        new_agent_tool_metadata (UpdateAgentToolMetadataRequest): New agent tool metadata data.

    Returns:
        AgentToolMetadata: Updated agent tool metadata.
    """
    for attr, value in new_agent_tool_metadata.model_dump(exclude_none=True).items():
        setattr(agent_tool_metadata, attr, value)
    db.commit()
    db.refresh(agent_tool_metadata)

    return agent_tool_metadata


def delete_agent_tool_metadata_by_id(db: Session, agent_tool_metadata_id: str) -> None:
    """
    Delete a agent tool metadata by its ID.

    Args:
        db (Session): Database session.
        agent_tool_metadata_id (str): Agent tool metadata ID.

    Returns:
        None
    """
    agent_tool_metadata = (
        db.query(AgentToolMetadata)
        .filter(AgentToolMetadata.id == agent_tool_metadata_id)
        .first()
    )
    db.delete(agent_tool_metadata)
    db.commit()
