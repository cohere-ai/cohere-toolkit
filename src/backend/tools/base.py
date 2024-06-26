from abc import abstractmethod
from typing import Any, Dict, List

from fastapi import Request

from backend.database_models.database import DBSessionDep


class BaseTool:
    """
    Abstract base class for all Tools.
    """

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool: ...

    @abstractmethod
    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]: ...


class BaseAuth:
    """
    Abstract base class for auth for tools
    """

    @classmethod
    @abstractmethod
    def get_auth_url(user_id: str) -> str: ...

    @classmethod
    @abstractmethod
    def is_auth_required(session: DBSessionDep, user_id: str) -> bool: ...

    @classmethod
    @abstractmethod
    def process_auth_token(request: Request, session: DBSessionDep) -> str: ...
