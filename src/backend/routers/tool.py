from fastapi import APIRouter, Depends, HTTPException, Request

from backend.config.routers import RouterName
from backend.config.tools import AVAILABLE_TOOLS
from backend.crud import agent as agent_crud
from backend.database_models.database import DBSessionDep
from backend.schemas.context import Context
from backend.schemas.tool import ManagedTool
from backend.services.agent import validate_agent_exists
from backend.services.context import get_context

router = APIRouter(prefix="/v1/tools")
router.name = RouterName.TOOL


@router.get("", response_model=list[ManagedTool])
def list_tools(
    request: Request,
    session: DBSessionDep,
    agent_id: str | None = None,
    ctx: Context = Depends(get_context),
) -> list[ManagedTool]:
    """
    List all available tools.

    Args:
        request (Request): The request to validate
        session (DBSessionDep): Database session.
        agent_id (str): Agent ID.
        ctx (Context): Context object.
    Returns:
        list[ManagedTool]: List of available tools.
    """
    user_id = ctx.get_user_id()
    logger = ctx.get_logger()

    all_tools = AVAILABLE_TOOLS.values()

    if agent_id is not None:
        agent_tools = []
        agent = validate_agent_exists(session, agent_id, user_id)

        for tool in agent.tools:
            agent_tools.append(AVAILABLE_TOOLS[tool])
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
