from concurrent import futures
from typing import Any, Dict, List, TypedDict

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from backend.database_models.database import get_session
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import ToolAuthException
from backend.tools.google_drive.auth import GoogleDriveAuth
from backend.tools.google_drive.constants import (
    CSV_MIMETYPE,
    DOC_FIELDS,
    GOOGLE_DRIVE_TOOL_ID,
    TEXT_MIMETYPE,
)

logger = LoggerFactory().get_logger()


class Service(TypedDict):
    service: Any
    creds: Credentials


def get_service(api: str, user_id: str, version: str = "v3") -> Service:
    # Get google credentials
    gdrive_auth = GoogleDriveAuth()
    agent_creator_auth_token = None

    session = next(get_session())
    if gdrive_auth.is_auth_required(session, user_id=user_id):
        session.close()
        raise ToolAuthException(
            "Sync GDrive Error: Agent creator credentials need to re-authenticate",
            GOOGLE_DRIVE_TOOL_ID,
        )

    agent_creator_auth_token = gdrive_auth.get_token(session=session, user_id=user_id)
    if agent_creator_auth_token is None:
        session.close()
        raise Exception("Sync GDrive Error: No agent creator credentials found")

    creds = Credentials(agent_creator_auth_token)
    service = build(api, version, credentials=creds, cache_discovery=False)
    session.close()
    return {"service": service, "creds": creds}


"""
GDrive GET file
"""


def perform_get_batch(file_ids: List[str], user_id: str) -> List[Dict[str, str]]:
    results = []

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures_list = [
            executor.submit(_get_file, file_id, user_id) for file_id in file_ids
        ]
        for future in futures.as_completed(futures_list):
            try:
                results.append(future.result())
            except Exception as e:
                raise e
    return results


def _get_file(file_id: str, user_id: str):
    (service,) = (
        get_service(api="drive", user_id=user_id)[key] for key in ("service",)
    )
    return (
        service.files()
        .get(
            fileId=file_id,
            fields=DOC_FIELDS,
            supportsAllDrives=True,
        )
        .execute()
    )

def process_shortcut_file(service: Any, file: Dict[str, str]) -> Dict[str, str]:
    if file["mimeType"] == "application/vnd.google-apps.shortcut":
        try:
            targetId = file["shortcutDetails"]["targetId"]
            targetFile = (
                service.files()
                .get(
                    fileId=targetId,
                    fields=DOC_FIELDS,
                    supportsAllDrives=True,
                )
                .execute()
            )
            return targetFile
        except Exception as error:
            file_id = file["id"]
            logger.error(
                event="An error occurred processing a shortcut file with id",
                file_id=file_id,
                type=type(error),
                error=error,
            )
            return {}
    else:
        return file


def extract_web_view_link(file: Dict[str, str]) -> str:
    return file.pop("webViewLink", "")

def extract_title(file: Dict[str, str]) -> str:
    return file.pop("name", "")


def extract_export_link(file: Dict[str, str]) -> str:
    export_links = file.pop("exportLinks", {})
    if TEXT_MIMETYPE in export_links:
        return export_links[TEXT_MIMETYPE]
    elif CSV_MIMETYPE in export_links:
        return export_links[CSV_MIMETYPE]
    return ""
