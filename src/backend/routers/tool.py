from fastapi import APIRouter, Depends

from backend.config.routers import RouterName
from backend.config.tools import get_available_tools
from backend.database_models.database import DBSessionDep
from backend.schemas.context import Context
from backend.schemas.params.agent import AgentIdQueryParam
from backend.schemas.tool import ToolDefinition
from backend.services.agent import validate_agent_exists
from backend.services.context import get_context

router = APIRouter(
    prefix="/v1/tools",
    tags=[RouterName.TOOL],
)
router.name = RouterName.TOOL


@router.get("", response_model=list[ToolDefinition])
def list_tools(
    *,
    agent_id: AgentIdQueryParam = None,
    session: DBSessionDep,
    ctx: Context = Depends(get_context),
) -> list[ToolDefinition]:
    """
    List all available tools.
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
        # Tools with auth implementation can be enabled and visible but not accessible (e.g., if secrets are not set).
        # Therefore, we need to set is_auth_required for these types of tools as well for the frontend.
        if (tool.is_available or tool.is_visible) and tool.auth_implementation is not None:
            try:
                tool_auth_service = tool.auth_implementation()

                tool.is_auth_required = tool_auth_service.is_auth_required(
                    session, user_id
                )
                tool.auth_url = tool_auth_service.get_auth_url(user_id)

                # Return access token to client when required by frontend
                # e.g: to enable Google Drive picker in client
                if tool.should_return_token:
                    tool.token = tool_auth_service.get_token(session, user_id)
            except Exception as e:
                logger.error(event=f"Error while fetching Tool Auth: {str(e)}")
                tool.is_auth_required = True
                tool.is_available = False
                tool.error_message = (
                    f"Error while calling Tool Auth implementation {str(e)}"
                )

    return all_tools
