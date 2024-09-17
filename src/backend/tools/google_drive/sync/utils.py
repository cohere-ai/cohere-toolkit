import io
import time
from concurrent import futures
from functools import wraps
from typing import Any, Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from backend.crud.agent_task import create_agent_task
from backend.database_models.database import get_session
from backend.services.logger.utils import LoggerFactory
from backend.tools.google_drive.auth import GoogleDriveAuth
from backend.tools.google_drive.constants import (
    CSV_MIMETYPE,
    DOC_FIELDS,
    NATIVE_EXTENSION_MAPPINGS,
    SEARCH_MIME_TYPES,
    TEXT_MIMETYPE,
)

"""
Get service
"""

logger = LoggerFactory().get_logger()


def get_service(api: str, user_id: str, version: str = "v3"):
    # Get google credentials
    gdrive_auth = GoogleDriveAuth()
    agent_creator_auth_token = None

    session = next(get_session())
    if gdrive_auth.is_auth_required(session, user_id=user_id):
        session.close()
        raise Exception(
            "Sync GDrive Error: Agent creator credentials need to re-authenticate"
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


def perform_get_single(file_id: str, user_id: str) -> Dict[str, str]:
    return _get_file(file_id=file_id, user_id=user_id)


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


"""
NON-NATIVE DOWNLOAD
"""


def perform_non_native_batch(service: Any, file_ids: List[str]) -> Dict[str, str]:
    tasks = []

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures_list = [
            executor.submit(_download_non_native_file, service, file_id)
            for file_id in file_ids
        ]
        for future in futures.as_completed(futures_list):
            try:
                tasks.append(future.result())
            except Exception as e:
                raise e

    return {
        "{}".format(task.get("file_id", "")): task.get("file_text", "")
        for task in tasks
    }


def perform_non_native_single(service: Any, file_id: str):
    return _download_non_native_file(service=service, file_id=file_id)


def _download_non_native_file(service: Any, file_id: str):
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)

    try:
        done = False
        while done is False:
            status, done = downloader.next_chunk(num_retries=5)
            logger.info(
                event="Downloading",
                file_id=file_id,
                status=status.progress(),
            )
        logger.info(
            event="Finished downloading",
            file_id=file_id,
        )
    except HttpError as error:
        logger.error(
            event="[Google Drive] Error downloading file",
            file_id=file_id,
            type=(type(error)),
            error=error,
        )
        return ""
    except Exception as error:
        logger.error(
            event="[Google Drive] Error downloading file",
            file_id=file_id,
            type=(type(error)),
            error=error,
        )
        return ""
    if file is None:
        return ""

    file_bytes = file.getvalue()
    return file_bytes


"""
OTHER
"""


def get_current_timestamp_in_ms(positive_offset: int = 0, negative_offset: int = 0):
    return int((time.time() + positive_offset - negative_offset) * 1000)


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


def extract_file_extension(file: Dict[str, str]) -> str:
    extension = file.pop("fileExtension", "")
    if not extension:
        # NOTE: Mean native file
        # ref. docs https://developers.google.com/drive/api/reference/rest/v3/files#File
        return NATIVE_EXTENSION_MAPPINGS[file["mimeType"]]
    return extension


def extract_title(file: Dict[str, str]) -> str:
    return file.pop("name", "")


def extract_export_link(file: Dict[str, str]) -> str:
    export_links = file.pop("exportLinks", {})
    if TEXT_MIMETYPE in export_links:
        return export_links[TEXT_MIMETYPE]
    elif CSV_MIMETYPE in export_links:
        return export_links[CSV_MIMETYPE]
    return ""


def extract_file_ids_from_target(activity: Dict[str, str]):
    file_ids = set()
    targets = activity["targets"]
    for target in targets:
        # NOTE: if not a drive item then skip
        if driveItem := target["driveItem"]:
            mimeType = driveItem["mimeType"]
            # NOTE: if mime type not being tracked then skip
            if mimeType in SEARCH_MIME_TYPES:
                file_id = driveItem["name"].split("/")[1]
                file_ids.add(file_id)
    return file_ids

def persist_agent_task(method):
    @wraps(method)
    def wrapper(
        self, file_id: str, index_name: str, user_id: str, agent_id: str, **kwargs
    ):
        task_id = self.request.id
        logger.info(
            event=f"Executing task id {self.request.id}, args: {self.request.args} kwargs: {self.request.kwargs}",
            agent_id=agent_id,
        )
        session = next(get_session())
        create_agent_task(session, agent_id=agent_id, task_id=task_id)
        session.close()
        return method(self, file_id, index_name, user_id, agent_id, **kwargs)

    return wrapper
