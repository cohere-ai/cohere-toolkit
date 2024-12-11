import datetime
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, Dict, List

from fastapi import Request
from pydantic import BaseModel

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.tool_auth import ToolAuth
from backend.schemas.tool import ToolDefinition
from backend.services.logger.utils import LoggerFactory
from backend.tools.utils.tools_checkers import check_tool_parameters

logger = LoggerFactory().get_logger()


class ToolErrorCode(StrEnum):
    HTTP_ERROR = "http_error"
    AUTH = "auth"
    OTHER = "other"


class ToolAuthException(Exception):
    def __init__(self, message, tool_id: str):
        self.message = message
        self.tool_id = tool_id

class ToolError(BaseModel, extra="allow"):
    type: ToolErrorCode = ToolErrorCode.OTHER
    success: bool = False
    text: str
    details: str = ""

class ParametersValidationMeta(type):
    """
    Metaclass to decorate all tools `call` methods with the parameter checker.
    """
    def __new__(cls, name, bases, class_dict):
        for attr_name, attr_value in class_dict.items():
            if callable(attr_value) and attr_name == "call":
                # Decorate methods with the parameter checker
                class_dict[attr_name] = check_tool_parameters(
                    lambda self: self.__class__.get_tool_definition()
                )(attr_value)
        return super().__new__(cls, name, bases, class_dict)


class BaseTool(metaclass=ParametersValidationMeta):
    """
    Abstract base class for all Tools.

    Attributes:
        ID (str): The name of the tool.
    """
    ID = None

    def __init__(self, *args, **kwargs):
        self._post_init_check()

    def _post_init_check(self):
        if self.ID is None:
            raise ValueError(f"{self.__name__} must have ID attribute defined.")

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        ...

    @classmethod
    @abstractmethod
    def get_tool_definition(cls) -> ToolDefinition:
        ...

    @classmethod
    def generate_error_message(cls) -> str | None:
        if cls.is_available():
            return None

        return f"{cls.__name__} is not available. Please make sure all required config variables are set."

    @classmethod
    def _handle_tool_specific_errors(cls, error: Exception, **kwargs: Any) -> None:
        ...

    @classmethod
    def get_tool_error(cls, details: str, text: str = "Error calling tool", error_type: ToolErrorCode = ToolErrorCode.OTHER):
        tool_error = ToolError(text=f"{text} {cls.ID}.", details=details, type=error_type).model_dump()
        logger.error(event=f"Error calling tool {cls.ID}", error=tool_error)
        return [tool_error]

    @classmethod
    def get_no_results_error(cls):
        return ToolError(text="No results found.", details="No results found for the given params.")

    @abstractmethod
    async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        ...


class BaseToolAuthentication(ABC):
    """
    Abstract base class for Tool Authentication.
    """

    def __init__(self, *args, **kwargs):
        self.BACKEND_HOST = Settings().get('auth.backend_hostname')
        self.FRONTEND_HOST = Settings().get('auth.frontend_hostname')
        self.AUTH_SECRET_KEY = Settings().get('auth.secret_key')

        self._post_init_check()

    def _post_init_check(self):
        if any(
                [
                    self.BACKEND_HOST is None,
                    self.FRONTEND_HOST is None,
                    self.AUTH_SECRET_KEY is None,
                ]
        ):
            raise ValueError(
                "Tool Authentication requires auth.backend_hostname, auth.frontend_hostname in configuration.yaml, "
                "and auth.secret_key in the secrets.yaml configuration files."
            )

    @abstractmethod
    def get_auth_url(self, user_id: str) -> str:
        ...

    def is_auth_required(self, session: DBSessionDep, user_id: str) -> bool:
        auth = tool_auth_crud.get_tool_auth(session, self.TOOL_ID, user_id)

        # Check Auth DNE
        if auth is None:
            return True

        # Check expired
        if datetime.datetime.now() > auth.expires_at:
            if self.try_refresh_token(session, user_id, auth):
                # Refreshed token successfully
                return False

            # Refresh failed, delete existing Auth
            tool_auth_crud.delete_tool_auth(session, user_id, self.TOOL_ID)
            return True

        # Check access_token is retrievable
        try:
            auth.access_token
            auth.refresh_token
        except Exception():
            # Retrieval failed, delete existing Auth
            tool_auth_crud.delete_tool_auth(session, user_id, self.TOOL_ID)
            return True

        # ToolAuth retrieved and is not expired
        return False

    @abstractmethod
    def try_refresh_token(
            self, session: DBSessionDep, user_id: str, tool_auth: ToolAuth
    ) -> bool:
        ...

    @abstractmethod
    def retrieve_auth_token(
            self, request: Request, session: DBSessionDep, user_id: str
    ) -> str:
        ...

    def get_token(self, session: DBSessionDep, user_id: str) -> str:
        tool_auth = tool_auth_crud.get_tool_auth(session, self.TOOL_ID, user_id)
        return tool_auth.access_token if tool_auth else None

    def delete_tool_auth(self, session: DBSessionDep, user_id: str) -> bool:
        try:
            tool_auth_crud.delete_tool_auth(session, user_id, self.TOOL_ID)
            return True
        except Exception as e:
            logger.error(
                event=f"BaseToolAuthentication: Error while deleting Tool Auth: {str(e)}"
            )
            raise
