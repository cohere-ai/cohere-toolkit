from sqlalchemy.orm import Session

from backend.database_models.agent_tool_metadata import AgentToolMetadata
from backend.schemas.agent import UpdateAgentToolMetadata


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


def get_agent_tool_metadata_by_agent_id_and_tool_name(
    db: Session, agent_id: str, tool_name: str
) -> AgentToolMetadata:
    """
    Get a agent tool metadata by its agent ID and tool name.
    """
    return (
        db.query(AgentToolMetadata)
        .filter(
            AgentToolMetadata.agent_id == agent_id,
            AgentToolMetadata.tool_name == tool_name,
        )
        .first()
    )


def update_agent_tool_metadata(
    db: Session,
    agent_tool_metadata: AgentToolMetadata,
    new_agent_tool_metadata: UpdateAgentToolMetadata,
) -> AgentToolMetadata:
    """
    Update a agent tool metadata.
    """
    for attr, value in new_agent_tool_metadata.model_dump(exclude_none=True).items():
        setattr(agent_tool_metadata, attr, value)
    db.commit()
    db.refresh(agent_tool_metadata)
    return agent_tool_metadata
