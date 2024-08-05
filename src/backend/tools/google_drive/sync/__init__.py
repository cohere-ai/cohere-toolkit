from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.services.logger.utils import LoggerFactory
from backend.tools.google_drive.auth import GoogleDriveAuth
from backend.tools.google_drive.constants import FOLDER_MIME_TYPE, SEARCH_MIME_TYPES
from backend.tools.google_drive.sync.actions import create
from backend.tools.google_drive.sync.utils import get_service
from backend.tools.google_drive.tool import GoogleDrive

logger = LoggerFactory().get_logger()


def handle_google_drive_sync(
    file_ids: List[str], agent_id: str, user_id: str, **kwargs
):
    index_name = "{}_{}".format(
        agent_id if agent_id is not None else user_id, GoogleDrive.NAME
    )
    [
        create.apply_async(
            args=[file_id, index_name, user_id],
            kwargs={
                "artifact_id": "",
                "skip_file_exists": True,
                **kwargs,
            },
        )
        for file_id in file_ids
    ]


def list_google_drive_artifacts_file_ids(
    session: Session, user_id: str, agent_artifacts: List[Dict[str, str]], verbose=False
):
    gdrive_auth = GoogleDriveAuth()
    if gdrive_auth.is_auth_required(session, user_id=user_id):
        raise Exception(
            "Sync GDrive Error: Agent creator credentials need to re-authenticate"
        )

    agent_creator_auth_token = gdrive_auth.get_token(session=session, user_id=user_id)
    if agent_creator_auth_token is None:
        raise Exception("Sync GDrive Error: No agent creator credentials found")

    (service,) = (
        get_service(api="drive", user_id=user_id)[key] for key in ("service",)
    )

    folder_artifacts = [x for x in agent_artifacts if x["type"] == "folder"]
    file_artifacts = [x for x in agent_artifacts if x["type"] != "folder"]

    file_ids = []
    for folder_artifact in folder_artifacts:
        file_ids += _recursively_list_google_drive_artifact_file_ids(
            service=service,
            user_id=user_id,
            artifact_id=folder_artifact["id"],
            verbose=verbose,
        )

    return [*file_ids, *[x["id"] for x in file_artifacts]]


def _recursively_list_google_drive_artifact_file_ids(
    service: Any,
    user_id: str,
    artifact_id: str,
    next_page_token: Optional[str] = None,
    verbose=False,
):
    if verbose:
        logger.info(
            event="[list_google_drive_artifacts_file_ids] Fetching artifacts for",
            artifact_id=artifact_id,
        )

    # fetch files and folders
    conditions = [
        "("
        + " or ".join(
            [
                f"mimeType = '{mime_type}'"
                for mime_type in [*SEARCH_MIME_TYPES, FOLDER_MIME_TYPE]
            ]
        )
        + ")",
        "'{}' in parents".format(artifact_id),
    ]
    q = " and ".join(conditions)

    fields = "nextPageToken, files(id, mimeType)"
    response = (
        service.files()
        .list(
            q=q,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields=fields,
            pageToken=next_page_token,
        )
        .execute()
    )

    artifacts = response["files"] if response else []
    folder_artifacts = [x["id"] for x in artifacts if x["mimeType"] == FOLDER_MIME_TYPE]
    file_artifacts = [x["id"] for x in artifacts if x["mimeType"] != FOLDER_MIME_TYPE]

    if response_next_page_token := response.get("nextPageToken", None):
        artifacts = [
            # existing files
            *file_artifacts,
            # same folder artifact with next page token
            *_recursively_list_google_drive_artifact_file_ids(
                service=service,
                user_id=user_id,
                artifact_id=artifact_id,
                next_page_token=response_next_page_token,
                verbose=verbose,
            ),
            # new folder artifacts with next page token
            *[
                x
                for new_artifact_id in folder_artifacts
                for x in _recursively_list_google_drive_artifact_file_ids(
                    service=service,
                    user_id=user_id,
                    artifact_id=new_artifact_id,
                    verbose=verbose,
                )
            ],
        ]

    return [
        # existing files
        *file_artifacts,
        # new folder artifacts with next page token
        *[
            x
            for new_artifact_id in folder_artifacts
            for x in _recursively_list_google_drive_artifact_file_ids(
                service=service,
                user_id=user_id,
                artifact_id=new_artifact_id,
                verbose=verbose,
            )
        ],
    ]
