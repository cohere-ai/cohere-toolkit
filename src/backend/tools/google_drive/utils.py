import io
from typing import Any, Dict, List

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from backend.services.logger import get_logger

from .constants import CSV_MIMETYPE, DOC_FIELDS, TEXT_MIMETYPE

logger = get_logger()


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


def process_non_native_files(
    service: Any, files: List[Dict[str, str]]
) -> Dict[str, str]:
    processed_files = []
    for file in files:
        if file["mimeType"] == "application/vnd.google-apps.shortcut":
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
        elif (
            file["mimeType"]
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            # do something. for now not supported.
            return _download_pdf(service=service, file_id=file["id"])
        else:
            processed_files.append(file)

    return processed_files


def _download_pdf(service: Any, file_id: str):
    try:
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

    except HttpError as error:
        logger.error("An error occurred: {}".format(error))
        file = None

    return file.getvalue() if file else None
