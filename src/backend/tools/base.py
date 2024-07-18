import base64
import os
from abc import abstractmethod
from typing import Any, Dict, List, Optional

from fastapi import Request

from backend.database_models.database import DBSessionDep
from backend.services.auth.crypto import encrypt
from backend.services.cache import cache_get_dict, cache_put


class BaseTool:
    """
    Abstract base class for all Tools.

    Attributes:
        NAME (str): The name of the tool.
    """

    NAME = None

    def __init__(self, *args, **kwargs):
        self._post_init_check()

    def _post_init_check(self):
        if any(
            [
                self.NAME is None,
            ]
        ):
            raise ValueError(f"{self.__name__} must have NAME attribute defined.")

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool: ...

    @classmethod
    @abstractmethod
    def _handle_tool_specific_errors(cls, error: Exception, **kwargs: Any) -> None:
        pass

    @abstractmethod
    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]: ...


class BaseToolAuthentication:
    """
    Abstract base class for Tool Authentication.
    """

    def __init__(self, *args, **kwargs):
        self.BACKEND_HOST = os.getenv("NEXT_PUBLIC_API_HOSTNAME")
        self.FRONTEND_HOST = os.getenv("FRONTEND_HOSTNAME")
        self.AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY")

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
                f"{self.__name__} requires NEXT_PUBLIC_API_HOSTNAME, FRONTEND_HOSTNAME, and AUTH_SECRET_KEY environment variables."
            )

    @abstractmethod
    def get_auth_url(self, user_id: str) -> str: ...

    @abstractmethod
    def is_auth_required(self, session: DBSessionDep, user_id: str) -> bool: ...

    @abstractmethod
    def retrieve_auth_token(
        self, request: Request, session: DBSessionDep, user_id: str
    ) -> str: ...

    @abstractmethod
    def get_token(self, user_id: str, session: DBSessionDep) -> Optional[str]:
        return None


class ToolAuthenticationCacheMixin:
    def insert_tool_auth_cache(self, user_id: str, tool_id: str) -> str:
        """
        Generates a token from a composite string formed by user_id + tool_id, and stores it in
        cache.
        """
        value = user_id + tool_id
        # Encrypt value with Fernet and convert to string
        key = encrypt(value).decode()

        # Existing cache entry
        if cache_get_dict(key):
            return key

        payload = {"user_id": user_id, "tool_id": tool_id}
        cache_put(key, payload)

        return key
