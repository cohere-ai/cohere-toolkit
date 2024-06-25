import os
from typing import Any, Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from backend.crud import tool_auth as tool_auth_crud
from backend.services.logger import get_logger
from backend.tools.base import BaseTool
from backend.tools.utils import async_download

from .constants import DOC_FIELDS, GOOGLE_DRIVE_TOOL_ID, SEARCH_LIMIT, SEARCH_MIME_TYPES
from .utils import extract_links

logger = get_logger()


class GoogleDrive(BaseTool):
    """
    Experimental (In development): Tool that searches Google Drive
    """

    @classmethod
    def is_available(cls) -> bool:
        vars = [
            "GOOGLE_DRIVE_CLIENT_ID",
            "GOOGLE_DRIVE_CLIENT_SECRET",
        ]
        return all(os.getenv(var) is not None for var in vars)

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Fetch from Google Drive
        """
        query = parameters.get("query", "")
        conditions = [
            "("
            + " or ".join(
                [f"mimeType = '{mime_type}'" for mime_type in SEARCH_MIME_TYPES]
            )
            + ")",
            "("
            + " or ".join([f"fullText contains '{word}'" for word in [query]])
            + ")",
        ]

        # Condition on folder if exists
        if gdrive_folder_id := parameters.get("folder_id", None):
            conditions.append(f"'{gdrive_folder_id}' in parents ")

        q = " and ".join(conditions)
        fields = f"nextPageToken, files({DOC_FIELDS})"
        auth = tool_auth_crud.get_tool_auth(
            kwargs.get("session"), GOOGLE_DRIVE_TOOL_ID, kwargs.get("user_id")
        )
        creds = Credentials(auth.encrypted_access_token.decode())

        search_results = []
        try:
            service = build("drive", "v3", credentials=creds)
            search_results = (
                service.files()
                .list(pageSize=SEARCH_LIMIT, q=q, fields=fields)
                .execute()
            )
        except Exception as e:
            logger.error(str(e))
            raise e

        results = []
        files = search_results.get("files", [])
        if not files:
            logger.debug("No files found.")
            return results

        id_to_urls = extract_links(files)
        id_to_texts = async_download.perform(id_to_urls, creds.token)

        """
        Insert into Compass
        """
        # todo

        return [dict({"text": text}) for text in id_to_texts.values()]
