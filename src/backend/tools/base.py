import datetime
from abc import ABC, abstractmethod
from typing import Any, Dict, List, get_args, get_origin

from fastapi import Request

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.database_models.database import DBSessionDep
from backend.database_models.tool_auth import ToolAuth
from backend.schemas.tool import ToolDefinition
from backend.services.logger.utils import LoggerFactory

logger = LoggerFactory().get_logger()

def check_type(param_value, type_description: str) -> bool:
    try:
        # Convert the type string into a type object
        expected_type = eval(type_description)
        return _check_type_recursive(param_value, expected_type)
    except Exception as e:
        print(f"Error during type checking: {e}")
        return False

def _check_type_recursive(value, expected_type) -> bool:
    origin = get_origin(expected_type)

    if origin is None:  # Base types (int, str, ...)
        return isinstance(value, expected_type)

    if origin is list:  # Check if the value is a list
        if not isinstance(value, list):
            return False
        element_type = get_args(expected_type)[0]
        return all(_check_type_recursive(item, element_type) for item in value)

    if origin is tuple:  # Tuples
        # trying to help to model with tuple type by converting lists to tuples, Cohere model passed tuples as list
        converted_value = tuple(value) if isinstance(value, list) else value
        if not isinstance(converted_value, tuple) or len(converted_value) != len(get_args(expected_type)):
            return False
        return all(
            _check_type_recursive(item, arg_type)
            for item, arg_type in zip(value, get_args(expected_type))
        )

    if origin is dict: # Dictionaries
        if not isinstance(value, dict):
            return False
        key_type, value_type = get_args(expected_type)
        return all(
            _check_type_recursive(k, key_type) and _check_type_recursive(v, value_type)
            for k, v in value.items()
        )

    # NOTE: Maybe we need to handle more types in the future, depends on the use in tools and models
    return False

def check_tool_parameters(tool_definition: ToolDefinition) -> None:
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            parameter_definitions = tool_definition(self).parameter_definitions
            passed_method_params = kwargs.get("parameters", {}) or args[0]
            # Validate parameters
            for param, rules in parameter_definitions.items():
                is_required = rules.get("required", False)
                if param not in passed_method_params:
                    if is_required:
                        raise ValueError(f"Model didn't pass required parameter: {param}")
                else:
                    value = passed_method_params[param]
                    if not value and is_required:
                        raise ValueError(f"Model passed empty value for required parameter: {param}")
                    if not check_type(value, rules["type"]):
                        raise TypeError(
                            f"Model passed invalid parameter. Parameter '{param}' must be of type {rules['type']}, but got {type(value).__name__}"
                        )

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class ParametersCheckingMeta(type):
    def __new__(cls, name, bases, dct):
        for attr_name, attr_value in dct.items():
            if callable(attr_value) and attr_name == "call":
                # Decorate methods with the parameter checker
                dct[attr_name] = check_tool_parameters(
                    lambda self: self.__class__.get_tool_definition()
                )(attr_value)
        return super().__new__(cls, name, bases, dct)


class BaseTool(metaclass=ParametersCheckingMeta):
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
    def is_available(cls) -> bool: ...

    @classmethod
    @abstractmethod
    def get_tool_definition(cls) -> ToolDefinition: ...

    @classmethod
    def generate_error_message(cls) -> str | None:
        if cls.is_available():
            return None

        return f"{cls.__name__} is not available. Please make sure all required config variables are set."

    @classmethod
    def _handle_tool_specific_errors(cls, error: Exception, **kwargs: Any) -> None: ...

    @abstractmethod
    async def call(
            self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]: ...


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


class ToolAuthException(Exception):
    def __init__(self, message, tool_id: str):
        self.message = message
        self.tool_id = tool_id
