from typing import Any, Dict, List

from google.auth.exceptions import RefreshError

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseTool

from .constants import GOOGLE_DRIVE_TOOL_ID

logger = LoggerFactory().get_logger()


class GoogleDrive(BaseTool):
    """
    Tool that searches Google Drive
    """

    NAME = GOOGLE_DRIVE_TOOL_ID

    CLIENT_ID = Settings().tools.google_drive.client_id
    CLIENT_SECRET = Settings().tools.google_drive.client_secret

    @classmethod
    def is_available(cls) -> bool:
        return cls.CLIENT_ID is not None and cls.CLIENT_ID is not None

    def _handle_tool_specific_errors(cls, error: Exception, **kwargs: Any):
        message = "[Google Drive] Tool Error: {}".format(str(error))

        if isinstance(error, RefreshError):
            session = kwargs["session"]
            user_id = kwargs["user_id"]
            tool_auth_crud.delete_tool_auth(
                db=session, user_id=user_id, tool_id=GOOGLE_DRIVE_TOOL_ID
            )

        logger.error(
            event="[Google Drive] Auth token error: Please refresh the page and re-authenticate."
        )
        raise Exception(message)

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        return []
