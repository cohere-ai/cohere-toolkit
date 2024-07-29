from backend.services.sync.env import env
from backend.tools.google_drive.constants import DOC_FIELDS, NATIVE_SEARCH_MIME_TYPES
from backend.tools.google_drive.utils import (
    extract_export_link,
    extract_title,
    extract_web_view_link,
    get_service,
    perform_get_single,
    perform_non_native_single,
    process_shortcut_file,
)
from backend.tools.utils import download


def get_file_details(file_id: str, user_id: str):
    """
    Return file bytes, web view link and title
    """
    # get service
    service, creds = (get_service(api="drive", user_id=user_id)[key] for key in ("service", "creds"))

    # get file details
    file_get = perform_get_single(file_id=file_id, user_id=user_id)
    if file_get["trashed"]:
        return None

    processed_file = process_shortcut_file(service, file_get)
    web_view_link = extract_web_view_link(processed_file)
    title = extract_title(file_get)

    # get file content bytes
    file_bytes = None
    if processed_file["mimeType"] in NATIVE_SEARCH_MIME_TYPES:
        # native files
        export_link = extract_export_link(processed_file)
        if export_link:
            file_text = download.perform_single(
                httpx_client=env().HTTPX_CLIENT,
                url=export_link,
                access_token=creds.token,
            )
            file_bytes = file_text.encode()
    else:
        # non-native files
        file_bytes = perform_non_native_single(service=service, file_id=processed_file["id"])

    return {
        "file_bytes": file_bytes,
        "web_view_link": web_view_link,
        "title": title,
    }


def get_folder_subfolders(folder_id: str, user_id: str):
    """
    Return folder's subfolders ids
    """
    # get service
    files = _list_items_recursively(folder_id=folder_id, user_id=user_id)

    if not files:
        return []

    return [
        *[x["id"] for x in files],
        *[y for x in files for y in get_folder_subfolders(folder_id=x["id"], user_id=user_id)],
    ]


def _list_items_recursively(
    folder_id: str,
    user_id: str,
    next_page_token: str = "",
):
    (service,) = (get_service(api="drive", user_id=user_id)[key] for key in ("service",))
    response = (
        service.files()
        .list(
            q="'{}' in parents and mimeType = 'application/vnd.google-apps.folder'".format(folder_id),
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            pageToken=next_page_token,
            fields="nextPageToken, files(id)",
        )
        .execute()
    )
    if response_next_page_token := response.get("nextPageToken", None):
        return [
            *response.get("files", []),
            *_list_items_recursively(
                folder_id=folder_id,
                user_id=user_id,
                next_page_token=response_next_page_token,
            ),
        ]
    return response.get("files", [])
