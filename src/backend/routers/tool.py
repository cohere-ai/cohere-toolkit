from fastapi import APIRouter, Depends, HTTPException, Request

from backend.config.routers import RouterName
from backend.config.tools import AVAILABLE_TOOLS
from backend.crud import agent as agent_crud
from backend.crud import tool as tool_crud
from backend.database_models.database import DBSessionDep
from backend.schemas.context import Context
from backend.schemas.tool import ManagedTool, ToolCreate, ToolDelete, ToolUpdate
from backend.services.context import get_context
from backend.services.request_validators import (
    validate_create_tool_request,
    validate_update_tool_request,
)

router = APIRouter(prefix="/v1/tools")
router.name = RouterName.TOOL


@router.post(
    "",
    response_model=ManagedTool,
    dependencies=[
        Depends(validate_create_tool_request),
    ],
)
def create_tool(tool: ToolCreate, session: DBSessionDep) -> ManagedTool:
    """
    Create a new tool.

    Args:
        model (ToolCreate): Tool data to be created.
        session (DBSessionDep): Database session.

    Returns:
        ManagedTool: Created tool.
    """

    return tool_crud.create_tool(session, tool)


@router.put(
    "/{tool_id}",
    response_model=ManagedTool,
    dependencies=[
        Depends(validate_update_tool_request),
    ],
)
def update_tool(
    tool_id: str, new_tool: ToolUpdate, session: DBSessionDep
) -> ManagedTool:
    """
    Update a tool by ID.

    Args:
        tool_id (str): Tool ID.
        new_tool (ToolUpdate): New tool data.
        session (DBSessionDep): Database session.

    Returns:
        ManagedTool: Updated tool.
    """
    tool = tool_crud.get_tool(session, tool_id)
    return tool_crud.update_tool(session, tool, new_tool)


@router.get("/{tool_id}", response_model=ManagedTool)
def get_tool(tool_id: str, session: DBSessionDep) -> ManagedTool:
    """
    Get a tool by ID.

    Args:
        tool_id (str): Tool ID.
        session (DBSessionDep): Database session.

    Returns:
        ManagedTool: Tool with the given ID.
    """
    tool = tool_crud.get_tool(session, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Model not found")
    return tool


@router.delete("/{tool_id}", response_model=ToolDelete)
def delete_tool(tool_id: str, session: DBSessionDep) -> ToolDelete:
    """
    Delete a tool by ID.

    Args:
        tool_id (str): Tool ID.
        session (DBSessionDep): Database session.

    Returns:
        ManagedTool: Deleted tool.
    """
    tool = tool_crud.get_tool(session, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    tool_crud.delete_tool(session, tool_id)

    return ToolDelete()


@router.get("", response_model=list[ManagedTool])
def list_tools(
    request: Request,
    session: DBSessionDep,
    agent_id: str | None = None,
    ctx: Context = Depends(get_context),
    all: bool = False,
) -> list[ManagedTool]:
    """
    List all available tools.

    Args:
        request (Request): Request object.
        session (DBSessionDep): Database session.
        agent_id (str): Agent ID.
        ctx (Context): Context object.
        all (bool): Flag to list all tools not only available.

    Returns:
        list[ManagedTool]: List of available tools.
    """
    if not all:
        all_tools = tool_crud.get_available_tools(session)
        if not all_tools:
            all_tools = AVAILABLE_TOOLS.values()
    else:
        all_tools = tool_crud.get_tools(session)
        if not all_tools:
            all_tools = AVAILABLE_TOOLS.values()
    if agent_id:
        agent = agent_crud.get_agent_by_id(session, agent_id)

    user_id = ctx.get_user_id()
    logger = ctx.get_logger()

    if agent_id is not None:
        agent_tools = []
        agent = agent_crud.get_agent_by_id(session, agent_id)

        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID: {agent_id} not found.",
            )

        if agent.associated_tools:
            all_tools = agent.associated_tools
        # for tool in agent.tools:
        #     agent_tools.append(AVAILABLE_TOOLS[tool])
        # all_tools = agent_tools

    for tool in all_tools:
        if tool.is_available and tool.auth_implementation is not None:
            try:
                tool_auth_service = tool.auth_implementation()

                tool.is_auth_required = tool_auth_service.is_auth_required(
                    session, user_id
                )
                tool.auth_url = tool_auth_service.get_auth_url(user_id)
                tool.token = tool_auth_service.get_token(session, user_id)
            except Exception as e:
                logger.error(event=f"Error while fetching Tool Auth: {str(e)}")

                tool.is_available = False
                tool.error_message = (
                    f"Error while calling Tool Auth implementation {str(e)}"
                )

    return all_tools
