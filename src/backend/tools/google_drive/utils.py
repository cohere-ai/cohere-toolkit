import io
import time
from concurrent import futures
from typing import Any, Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from backend.database_models.database import get_session
from backend.services.logger.utils import get_logger
from backend.tools.google_drive.auth import GoogleDriveAuth
from backend.tools.google_drive.constants import (
    CSV_MIMETYPE,
    DOC_FIELDS,
    NATIVE_EXTENSION_MAPPINGS,
    TEXT_MIMETYPE,
)

logger = get_logger()

"""
Get service
"""


def get_service(api: str, user_id: str, version: str = "v3"):
    # Get google credentials
    gdrive_auth = GoogleDriveAuth()
    agent_creator_auth_token = None

    session = next(get_session())
    agent_creator_auth_token = gdrive_auth.get_token(session=session, user_id=user_id)
    if agent_creator_auth_token is None:
        raise Exception("Sync GDrive Error: No agent creator credentials found")

    if gdrive_auth.is_auth_required(session, user_id=user_id):
        raise Exception(
            "Sync GDrive Error: Agent creator credentials need to re-authenticate"
        )

    creds = Credentials(agent_creator_auth_token)
    service = build(api, version, credentials=creds, cache_discovery=False)
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
            logger.info("Downloading {}: {}%".format(file_id, status.progress()))
        logger.info("Finished downloading {}".format(file_id))
    except HttpError as error:
        logger.error(f"[Google Drive] Error downloading file: {str(error)}")
        return ""
    except Exception as e:
        logger.error(
            f"[Google Drive] Error downloading file: {file_id}: {type(e)} -- {e}"
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
        except Exception as e:
            message = "An error occurred processing a shortcut file with id {}: {} -- {}".format(
                file["id"], type(e), e
            )
            logger.error(message)
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


def extract_export_link(file: Dict[str, str]) -> Dict[str, str]:
    export_links = file.pop("exportLinks", {})
    if TEXT_MIMETYPE in export_links:
        return export_links[TEXT_MIMETYPE]
    elif CSV_MIMETYPE in export_links:
        return export_links[CSV_MIMETYPE]
    return ""
