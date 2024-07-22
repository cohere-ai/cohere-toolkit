from typing import Optional

from fastapi import APIRouter, HTTPException, Request

from backend.config.routers import RouterName
from backend.config.tools import AVAILABLE_TOOLS
from backend.crud import agent as agent_crud
from backend.database_models.database import DBSessionDep
from backend.schemas.tool import ManagedTool
from backend.services.auth.utils import get_header_user_id
from backend.services.logger import get_logger

logger = get_logger()

router = APIRouter(prefix="/v1/tools")
router.name = RouterName.TOOL


@router.get("", response_model=list[ManagedTool])
def list_tools(
    request: Request, session: DBSessionDep, agent_id: str | None = None
) -> list[ManagedTool]:
    """
    List all available tools.

    Returns:
        list[ManagedTool]: List of available tools.
    """
    all_tools = AVAILABLE_TOOLS.values()
    if agent_id:
        agent_tools = []
        agent = agent_crud.get_agent_by_id(session, agent_id)

        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID: {agent_id} not found.",
            )

        for tool in agent.tools:
            agent_tools.append(AVAILABLE_TOOLS[tool])
        all_tools = agent_tools

    user_id = get_header_user_id(request)
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
                logger.error(f"Error while fetching Tool Auth: {str(e)}.")

    return all_tools
