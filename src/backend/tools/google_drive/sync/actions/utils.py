from functools import wraps
from typing import Dict, List, Optional

from backend.services.sync.env import env
from backend.tools.google_drive.constants import (
    NATIVE_SEARCH_MIME_TYPES,
    SEARCH_MIME_TYPES,
)
from backend.tools.google_drive.sync.utils import (
    extract_export_link,
    extract_file_extension,
    extract_title,
    extract_web_view_link,
    get_service,
    perform_get_single,
    perform_non_native_single,
    process_shortcut_file,
)
from backend.services.logger.utils import LoggerFactory
from backend.tools.utils import download
from backend.crud.agent_task import create_agent_task
from backend.database_models.database import get_session

logger = LoggerFactory().get_logger()


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


def get_file_details(
    file_id: str, user_id: str, include_permissions=False, just_title=False
):
    """
    Return file bytes, web view link and title
    """
    # get service
    service, creds = (
        get_service(api="drive", user_id=user_id)[key] for key in ("service", "creds")
    )

    # get file details
    file_get = perform_get_single(file_id=file_id, user_id=user_id)
    if file_get["trashed"]:
        return None

    processed_file = process_shortcut_file(service, file_get)
    if processed_file["mimeType"] not in SEARCH_MIME_TYPES:
        return None

    extension = extract_file_extension(processed_file)
    web_view_link = extract_web_view_link(processed_file)
    title = extract_title(processed_file)

    if just_title:
        return {"title": title}

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
        file_bytes = perform_non_native_single(
            service=service, file_id=processed_file["id"]
        )

    permissions = []
    if include_permissions:
        permissions = list_permissions(file_id=file_id, user_id=user_id)

    return {
        "file_bytes": file_bytes,
        "extension": extension,
        "web_view_link": web_view_link,
        "title": title,
        "permissions": permissions,
    }


def list_permissions(file_id: str, user_id: str, next_page_token: Optional[str] = None):
    (service,) = (
        get_service(api="drive", user_id=user_id)[key] for key in ("service",)
    )
    response = (
        service.permissions()
        .list(
            fileId=file_id,
            supportsAllDrives=True,
            pageToken=next_page_token,
            fields="permissions(emailAddress, type, domain), nextPageToken",
        )
        .execute()
    )
    if response_next_page_token := response.get("nextPageToken", None):
        return [
            *_format_permissions(response.get("permissions", [])),
            *list_permissions(
                file_id=file_id,
                user_id=user_id,
                next_page_token=response_next_page_token,
            ),
        ]
    return _format_permissions(response.get("permissions", []))


def check_if_file_exists_in_artifact(
    file_id: str, artifact_id: str, user_id: str, title: str
):
    (service,) = (
        get_service(api="drive", user_id=user_id)[key] for key in ("service",)
    )
    response = (
        service.files()
        .list(
            q="'{}' in parents and name = '{}'".format(artifact_id, title),
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        )
        .execute()
    )

    if files := response.get("files", None):
        found_file = [x for x in files if x["id"] == file_id]
        if found_file:
            return True
    return False


def _format_permissions(permissions: List[Dict[str, str]]):
    return [
        *[
            {"id": x["emailAddress"], "type": x["type"]}
            for x in permissions
            if "emailAddress" in x
        ],
        *[{"id": x["domain"], "type": x["type"]} for x in permissions if "domain" in x],
        *[{"id": x["group"], "type": x["type"]} for x in permissions if "group" in x],
    ]
