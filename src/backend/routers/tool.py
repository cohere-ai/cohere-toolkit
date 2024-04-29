from fastapi import APIRouter, Depends

from backend.config.tools import AVAILABLE_TOOLS
from backend.models import get_session
from backend.schemas.tool import ManagedTool

router = APIRouter(prefix="/tools", dependencies=[Depends(get_session)])


@router.get("/", response_model=list[ManagedTool])
def list_tools() -> list[ManagedTool]:
    """
    List all available tools.

    Returns:
        list[ManagedTool]: List of available tools.
    """
    return AVAILABLE_TOOLS.values()
