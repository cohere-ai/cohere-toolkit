from typing import Any, Dict, List

from .constants import CSV_MIMETYPE, DOC_FIELDS, TEXT_MIMETYPE


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


def process_shortcut_files(service: Any, files: List[Dict[str, str]]) -> Dict[str, str]:
    processed_files = []
    for file in files:
        if file["mimeType"] == "application/vnd.google-apps.shortcut":
            targetId = file["shortcutDetails"]["targetId"]
            targetFile = (
                service.files().get(fileId=targetId, fields=DOC_FIELDS).execute()
            )
            processed_files.append(targetFile)
        else:
            processed_files.append(file)
    return processed_files
