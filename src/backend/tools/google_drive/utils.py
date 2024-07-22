import io
import time
from concurrent import futures
from typing import Any, Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from backend.services.compass import Compass
from backend.services.logger import get_logger
from backend.tools.google_drive.constants import DOC_FIELDS

from .constants import CSV_MIMETYPE, DOC_FIELDS, TEXT_MIMETYPE

logger = get_logger()

"""
NATIVE DOWNLOAD
"""


def perform_native_batch(
    file_ids: List[str], creds: Credentials
) -> List[Dict[str, str]]:
    results = []

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures_list = [
            executor.submit(_get_native_file, file_id, creds) for file_id in file_ids
        ]
        for future in futures.as_completed(futures_list):
            try:
                results.append(future.result())
            except Exception as e:
                raise e
    return results


def perform_native_single(file_id: str, creds: Credentials) -> Dict[str, str]:
    return _get_native_file(file_id=file_id, creds=creds)


def _get_native_file(file_id: str, creds: Credentials):
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
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
    compass = Compass()
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)

    try:
        done = False
        while done is False:
            status, done = downloader.next_chunk(num_retries=5)
            logger.info("Downloading {}: {}%".format(file_id, status.progress()))
        logger.info("Finished downloading {}".format(file_id))
    except HttpError as e:
        message = "An error occurred downloading file with id {}: {} -- {}".format(
            file_id, type(e), e
        )
        logger.error(message)
        return ""
    except Exception as e:
        message = "An error occurred downloading file with id {}: {} -- {}".format(
            file_id, type(e), e
        )
        logger.error(message)
        return ""

    if file is None:
        return ""

    file_bytes = file.getvalue()
    logger.info("Initiated processing raw file bytes for {}".format(file_id))
    try:
        file_text = compass.invoke(
            action=Compass.ValidActions.PROCESS_FILE,
            parameters={"file_id": file_id, "file_text": file_bytes},
        )[0].content["text"]
        logger.info("Finished processing raw file bytes for {}".format(file_id))
        return file_text
    except Exception as e:
        message = "An error occurred invoking Compass to process file with id {}: {} -- {}".format(
            file_id, type(e), e
        )
        logger.error(message)
        return ""


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


def extract_title(file: Dict[str, str]) -> str:
    return file.pop("name", "")


def extract_export_link(file: Dict[str, str]) -> Dict[str, str]:
    export_links = file.pop("exportLinks", {})
    if TEXT_MIMETYPE in export_links:
        return export_links[TEXT_MIMETYPE]
    elif CSV_MIMETYPE in export_links:
        return export_links[CSV_MIMETYPE]
    return ""
