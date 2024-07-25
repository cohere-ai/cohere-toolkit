from sqlalchemy.orm import Session

from backend.database_models import Agent, AgentTool, Tool
from backend.schemas.tool import ToolCreate as ToolCreateSchema
from backend.schemas.tool import ToolUpdate as ToolUpdateSchema
from backend.services.transaction import validate_transaction


@validate_transaction
def create_tool(db: Session, tool: ToolCreateSchema) -> Tool:
    """
    Create a new tool.

    Args:
        db (Session): Database session.
        tool (toolSchema): tool data to be created.

    Returns:
        tool: Created tool.
    """

    tool = Tool(**tool.model_dump(exclude_none=True))
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool


def get_tool(db: Session, tool_id: str) -> Tool:
    """
    Get a tool by ID.

    Args:
        db (Session): Database session.
        tool_id (str): tool ID.

    Returns:
        tool: tool with the given ID.
    """
    return db.query(Tool).filter(Tool.id == tool_id).first()


def get_tool_by_name(db: Session, tool_name: str) -> Tool:
    """
    Get a tool by tool_name.

    Args:
        db (Session): Database session.
        tool_name (str): tool Name.

    Returns:
        tool: tool with the given name.
    """
    return db.query(Tool).filter(Tool.name == tool_name).first()


def get_tools(db: Session, offset: int = 0, limit: int = 100) -> list[Tool]:
    """
    List all tools.

    Args:
        db (Session): Database session.
        offset (int): Offset to start the list.
        limit (int): Limit of tools to be listed.

    Returns:
        list[tool]: List of tools.
    """
    return db.query(Tool).order_by(Tool.name).offset(offset).limit(limit).all()


def get_available_tools(db: Session, offset: int = 0, limit: int = 100) -> list[Tool]:
    """
    List all available tools.

    Args:
        db (Session): Database session.
        offset (int): Offset to start the list.
        limit (int): Limit of tools to be listed.

    Returns:
        list[tool]: List of available tools.
    """
    all_tools = db.query(Tool).all()
    return [tool for tool in all_tools if tool.is_available][offset : offset + limit]


def get_tools_by_agent_id(
    db: Session, agent_id: str, offset: int = 0, limit: int = 100
) -> list[Tool]:
    """
    List all tools by user id

    Args:
        db (Session): Database session.
        agent_id (str): User ID
        offset (int): Offset to start the list.
        limit (int): Limit of tools to be listed.

    Returns:
        list[tool]: List of tools.
    """
    return (
        db.query(Tool)
        .join(
            AgentTool,
            Tool.id == AgentTool.tool_id,
        )
        .filter(AgentTool.agent_id == agent_id)
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_available_tools_by_agent_id(
    db: Session, agent_id: str, offset: int = 0, limit: int = 100
) -> list[Tool]:
    """
    List all tools by user id

    Args:
        db (Session): Database session.
        agent_id (str): User ID
        offset (int): Offset to start the list.
        limit (int): Limit of tools to be listed.

    Returns:
        list[tool]: List of tools.
    """
    agent_tools = (
        db.query(Tool)
        .join(
            AgentTool,
            Tool.id == AgentTool.tool_id,
        )
        .filter(AgentTool.agent_id == agent_id)
        .limit(limit)
        .offset(offset)
        .all()
    )

    return [tool for tool in agent_tools if tool.is_available][offset : offset + limit]


def get_agent_tool_by_name(db: Session, agent_id: str, tool_name: str) -> Tool:
    """
    Get a tool by agent_id and tool_name.

    Args:
        db (Session): Database session.
        agent_id (str): Agent ID.
        tool_name (str): Tool Name.

    Returns:
        tool: tool with the given name.
    """
    return (
        db.query(Tool)
        .join(
            AgentTool,
            Tool.id == AgentTool.tool_id,
        )
        .filter(AgentTool.agent_id == agent_id)
        .filter(Tool.name == tool_name)
        .first()
    )


@validate_transaction
def update_tool(db: Session, tool: Tool, new_tool: ToolUpdateSchema) -> Tool:
    """
    Update a tool by ID.

    Args:
        db (Session): Database session.
        tool (tool): tool to be updated.
        new_tool (tool): New tool data.

    Returns:
        tool: Updated tool.
    """
    for attr, value in new_tool.model_dump(exclude_none=True).items():
        setattr(tool, attr, value)
    db.commit()
    db.refresh(tool)
    return tool


@validate_transaction
def assign_tool_to_agent(
    db: Session, tool: Tool, agent: Agent, tool_config: dict = {}
) -> Agent:
    """
    Assign a tool to an agent.

    Args:
        db (Session): Database session.
        agent (Agent): Agent to assign the tool.
        tool (Tool): Tool to be assigned.
        tool_config (dict): Tool configuration

    Returns:
        Agent: Agent with the assigned tool.
    """
    agent_tool = AgentTool(agent_id=agent.id, tool_id=tool.id, tool_config=tool_config)
    db.add(agent_tool)
    db.commit()
    db.refresh(agent)
    return agent


@validate_transaction
def remove_tool_from_agent(db: Session, tool: Tool, agent: Agent) -> Agent:
    """
    Remove a tool from an agent.

    Args:
        db (Session): Database session.
        agent (Agent): Agent to remove the tool.
        tool (Tool): Tool to be removed.

    Returns:
        Agent: Agent without the removed tool.
    """
    agent_tool = (
        db.query(AgentTool)
        .filter(AgentTool.agent_id == agent.id)
        .filter(AgentTool.tool_id == tool.id)
        .first()
    )
    db.delete(agent_tool)
    db.commit()
    db.refresh(agent)
    return agent


@validate_transaction
def remove_all_tools_from_agent(db: Session, agent: Agent) -> Agent:
    """
    Remove all tools from an agent.

    Args:
        db (Session): Database session.
        agent (Agent): Agent to remove the tools.

    Returns:
        Agent: Agent without the removed tools.
    """
    agent_tools = db.query(AgentTool).filter(AgentTool.agent_id == agent.id)
    agent_tools.delete()
    db.commit()
    db.refresh(agent)
    return agent


@validate_transaction
def delete_tool(db: Session, tool_id: str) -> None:
    """
    Delete a tool by ID.

    Args:
        db (Session): Database session.
        tool_id (str): tool ID.
    """
    tool = db.query(Tool).filter(Tool.id == tool_id)
    tool.delete()
    db.commit()
