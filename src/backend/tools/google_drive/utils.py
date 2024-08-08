import asyncio
import io
from typing import Any, Dict, List

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from backend.services.compass import Compass
from backend.services.logger.utils import LoggerFactory

from .constants import CSV_MIMETYPE, DOC_FIELDS, TEXT_MIMETYPE

logger = LoggerFactory().get_logger()


def extract_links(files: List[Dict[str, str]]) -> Dict[str, str]:
    id_to_urls = dict()
    for _file in files:
        export_links = _file.pop("exportLinks", {})
        id = _file.get("id")
        if id is None:
            continue

        if TEXT_MIMETYPE in export_links:
            id_to_urls[id] = export_links[TEXT_MIMETYPE]
        elif CSV_MIMETYPE in export_links:
            id_to_urls[id] = export_links[CSV_MIMETYPE]
    return id_to_urls


def extract_web_view_links(files: List[Dict[str, str]]) -> Dict[str, str]:
    id_to_urls = dict()
    for _file in files:
        web_view_link = _file.pop("webViewLink", "")
        id = _file.get("id")
        if id is None:
            continue

        id_to_urls[id] = web_view_link
    return id_to_urls


def extract_titles(files: List[Dict[str, str]]) -> Dict[str, str]:
    id_to_names = dict()
    for _file in files:
        name = _file.pop("name", "")
        id = _file.get("id")
        if id is None:
            continue

        id_to_names[id] = name
    return id_to_names


def process_shortcut_files(service: Any, files: List[Dict[str, str]]) -> Dict[str, str]:
    processed_files = []
    for file in files:
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
                processed_files.append(targetFile)
            except Exception as _e:
                continue
        else:
            processed_files.append(file)

    return processed_files


async def non_native_files_perform(
    service: Any, compass: Compass, files: List[Dict[str, str]]
) -> dict[str, str]:
    return await _download_non_native_files(service, compass, files)


async def _download_non_native_files(
    service: Any, compass: Compass, files: List[Dict[str, str]]
):
    tasks = [_download_non_native_file(service, compass, file["id"]) for file in files]
    return {id: text for (id, text) in (await asyncio.gather(*tasks))}


async def _download_non_native_file(service: Any, compass: Compass, file_id: str):
    try:
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            _status, done = downloader.next_chunk()
    except HttpError as error:
        logger.error(f"[Google Drive] Error downloading file: {str(error)}")
        file = None

    if file is None:
        return None

    file_bytes = file.getvalue()
    file_text = compass.invoke(
        action=Compass.ValidActions.PROCESS_FILE,
        parameters={"file_id": file_id, "file_text": file_bytes},
    )[0].content["text"]
    return (file_id, file_text)
