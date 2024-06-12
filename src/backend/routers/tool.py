from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.config.routers import RouterName
from backend.config.tools import AVAILABLE_TOOLS
from backend.crud import agent as agent_crud
from backend.database_models.database import DBSessionDep
from backend.schemas.tool import ManagedTool

router = APIRouter(prefix="/v1/tools")
router.name = RouterName.TOOL


@router.get("", response_model=list[ManagedTool])
def list_tools(session: DBSessionDep, agent_id: str | None = None) -> list[ManagedTool]:
    """
    List all available tools.

    Returns:
        list[ManagedTool]: List of available tools.
    """
    if agent_id:
        agent_tools = []
        agent = agent_crud.get_agent(session, agent_id)

        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID: {agent_id} not found.",
            )

        for tool in agent.tools:
            agent_tools.append(AVAILABLE_TOOLS[tool])
        return agent_tools

    return AVAILABLE_TOOLS.values()
