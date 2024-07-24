from fastapi import HTTPException

from backend.crud import tool as tool_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.tool import (
    COMMUNITY_TOOLS_MODULE,
    DEFAULT_AUTH_MODULE,
    DEFAULT_TOOLS_MODULE,
    Tool,
)
from backend.services.get_module_class import get_module_class
from backend.tools.base import BaseTool, BaseToolAuthentication


def validate_implementation_class_name(implementation_class_name: str) -> BaseTool:
    """
    Validate the implementation class name.

    Args:
        implementation_class_name (str): Implementation class name.

    Returns:

        Any: Implementation class.
    """
    cls = get_module_class(DEFAULT_TOOLS_MODULE, implementation_class_name)
    if not cls:
        cls = get_module_class(COMMUNITY_TOOLS_MODULE, implementation_class_name)
    if not cls:
        raise HTTPException(
            status_code=400, detail=f"Tool class not found: {implementation_class_name}"
        )

    return cls


def validate_auth_class_name(auth_class_name: str) -> BaseToolAuthentication:
    """
    Validate the auth class name.

    Args:
        auth_class_name (str): Auth class name.

    Returns:
        Any : Auth class.
    """
    cls = get_module_class(DEFAULT_AUTH_MODULE, auth_class_name)
    if not cls:
        raise HTTPException(
            status_code=400, detail=f"Auth class not found: {auth_class_name}"
        )

    return cls
