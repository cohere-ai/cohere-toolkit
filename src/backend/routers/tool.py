from fastapi import APIRouter

from backend.config.routers import RouterName
from backend.config.tools import AVAILABLE_TOOLS
from backend.schemas.tool import ManagedTool

router = APIRouter(prefix="/v1/tools")
router.name = RouterName.TOOL


@router.get("", response_model=list[ManagedTool])
def list_tools() -> list[ManagedTool]:
    """
    List all available tools.

    Returns:
        list[ManagedTool]: List of available tools.
    """
    return AVAILABLE_TOOLS.values()
