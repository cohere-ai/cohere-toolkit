import time
from typing import Any, Dict, List

from fastapi import HTTPException
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.services.compass import Compass
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseTool
from backend.tools.utils import async_download, parallel_get_files

from .constants import (
    COMPASS_UPDATE_INTERVAL,
    DOC_FIELDS,
    GOOGLE_MAIL_TOOL_ID,
    NATIVE_SEARCH_MIME_TYPES,
    NON_NATIVE_SEARCH_MIME_TYPES,
    SEARCH_LIMIT,
    SEARCH_MIME_TYPES,
)
from .utils import (
    extract_links,
    extract_titles,
    extract_web_view_links,
    non_native_files_perform,
    process_shortcut_files,
)

logger = LoggerFactory().get_logger()


class GoogleMail(BaseTool):
    """
    Tool that searches Google Mail
    """

    NAME = GOOGLE_MAIL_TOOL_ID

    CLIENT_ID = Settings().tools.google_drive.client_id
    CLIENT_SECRET = Settings().tools.google_drive.client_secret

    @classmethod
    def is_available(cls) -> bool:
        return cls.CLIENT_ID is not None and cls.CLIENT_ID is not None

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        return []
