import logging
from typing import Any, Dict, List

from fastapi.security import OAuth2PasswordBearer

from backend.tools.base import BaseTool


class GoogleDrive(BaseTool):
    """
    Tool that searches Google Drive with an oauth token
    """

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def is_available(cls) -> bool:
        return True

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")
        # TODO this should call google drive with the oauth token stored in the DB
        # If it is expired it should refresh the token 
        result = []
        return result