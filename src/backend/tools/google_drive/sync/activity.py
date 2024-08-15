from concurrent import futures
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.tools.google_drive.auth import GoogleDriveAuth
from backend.tools.google_drive.constants import (
    ACTIVITY_TRACKING_WINDOW,
    GoogleDriveActions,
)
from backend.tools.google_drive.sync.actions import (
    create,
    delete,
    edit,
    move,
    permission_change,
    rename,
    restore,
)
from backend.tools.google_drive.sync.utils import (
    extract_file_ids_from_target,
    get_current_timestamp_in_ms,
    get_service,
)
from backend.tools.google_drive.tool import GoogleDrive


def handle_google_drive_activity_event(
    event_type: str, activity: Dict[str, str], agent_id: str, user_id: str, **kwargs
):
    index_name = "{}_{}".format(
        agent_id if agent_id is not None else user_id, GoogleDrive.NAME
    )
    file_ids = extract_file_ids_from_target(activity=activity)
    if not file_ids:
        return

    match event_type:
        case GoogleDriveActions.CREATE.value:
            [
                create.apply_async(
                    args=[file_id, index_name, user_id, agent_id],
                    kwargs={
                        "artifact_id": kwargs["artifact_id"],
                        **kwargs,
                    },
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.EDIT.value:
            [
                edit.apply_async(
                    args=[file_id, index_name, user_id, agent_id],
                    kwargs={
                        "artifact_id": kwargs["artifact_id"],
                        **kwargs,
                    },
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.MOVE.value:
            [
                move.apply_async(
                    args=[file_id, index_name, user_id, agent_id],
                    kwargs={
                        "artifact_id": kwargs["artifact_id"],
                        **kwargs,
                    },
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.RENAME.value:
            [
                rename.apply_async(
                    args=[file_id, index_name, user_id, agent_id],
                    kwargs={
                        **kwargs,
                    },
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.DELETE.value:
            [
                delete.apply_async(
                    args=[file_id, index_name, user_id, agent_id],
                    kwargs=kwargs,
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.RESTORE.value:
            [
                restore.apply_async(
                    args=[file_id, index_name, user_id, agent_id],
                    kwargs=kwargs,
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.PERMISSION_CHANGE.value:
            [
                permission_change.apply_async(
                    args=[file_id, index_name, user_id, agent_id],
                    kwargs={
                        "artifact_id": kwargs["artifact_id"],
                        **kwargs,
                    },
                )
                for file_id in file_ids
            ]
        case _:
            raise Exception("This action is not tracked for Google Drive")


def query_google_drive_activity(
    session: Session, user_id: str, agent_artifacts: List[Dict[str, str]]
):
    gdrive_auth = GoogleDriveAuth()
    agent_creator_auth_token = gdrive_auth.get_token(session=session, user_id=user_id)
    if agent_creator_auth_token is None:
        raise Exception(
            f"Sync GDrive Error: No agent creator credentials found user id: {user_id}"
        )

    if gdrive_auth.is_auth_required(session, user_id=user_id):
        raise Exception(
            "Sync GDrive Error: Agent creator credentials need to re-authenticate"
        )

    (service,) = (
        get_service(api="driveactivity", version="v2", user_id=user_id)[key]
        for key in ("service",)
    )

    activity_ts_filter = get_current_timestamp_in_ms(
        negative_offset=ACTIVITY_TRACKING_WINDOW
    )
    activities = {}
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures_list = [
            executor.submit(_get_activity, service, artifact, activity_ts_filter)
            for artifact in agent_artifacts
        ]
        for future in futures.as_completed(futures_list):
            try:
                (artifact_id, artifact_activities) = (
                    future.result()[key] for key in ("id", "activities")
                )
                activities[artifact_id] = artifact_activities
            except Exception as e:
                raise e

    return activities


def _get_activity(
    service: Any,
    artifact: Dict[str, str],
    activity_ts_filter: int,
    next_page_token: Optional[str] = None,
):
    artifact_id = artifact["id"]
    artifact_type = artifact["type"]
    response = (
        service.activity()
        .query(
            body={
                "filter": "time >= {} AND detail.action_detail_case:({})".format(
                    activity_ts_filter,
                    " ".join([e.value.upper() for e in GoogleDriveActions]),
                ),
                **(
                    {"ancestorName": "items/{}".format(artifact_id)}
                    if artifact_type == "folder"
                    else {}
                ),
                **(
                    {"itemName": "items/{}".format(artifact_id)}
                    if artifact_type != "folder"
                    else {}
                ),
                "pageToken": next_page_token,
                "consolidationStrategy": {
                    "legacy": {},
                },
            }
        )
        .execute()
    )
    if response_next_page_token := response.get("nextPageToken", None):
        return {
            "id": artifact_id,
            "activities": [
                *response.get("activities", []),
                *_get_activity(
                    service=service,
                    artifact=artifact,
                    activity_ts_filter=activity_ts_filter,
                    next_page_token=response_next_page_token,
                )["activities"],
            ],
        }
    return {
        "id": artifact_id,
        "activities": response["activities"] if response else [],
    }
