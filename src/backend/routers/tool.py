from fastapi import APIRouter, Depends, Request

from backend.config.routers import RouterName
from backend.config.tools import get_available_tools
from backend.database_models.database import DBSessionDep
from backend.schemas.context import Context
from backend.schemas.tool import ToolDefinition
from backend.services.agent import validate_agent_exists
from backend.services.context import get_context

router = APIRouter(prefix="/v1/tools")
router.name = RouterName.TOOL


@router.get("", response_model=list[ToolDefinition])
def list_tools(
    request: Request,
    session: DBSessionDep,
    agent_id: str | None = None,
    ctx: Context = Depends(get_context),
) -> list[ToolDefinition]:
    """
    List all available tools.

    Args:
        request (Request): The request to validate
        session (DBSessionDep): Database session.
        agent_id (str): Agent ID.
        ctx (Context): Context object.
    Returns:
        list[ToolDefinition]: List of available tools.
    """
    user_id = ctx.get_user_id()
    logger = ctx.get_logger()

    available_tools = get_available_tools()
    all_tools = list(available_tools.values())

    if agent_id is not None:
        agent_tools = []
        agent = validate_agent_exists(session, agent_id, user_id)

        for tool in agent.tools:
            agent_tools.append(available_tools[tool])
        all_tools = agent_tools

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
