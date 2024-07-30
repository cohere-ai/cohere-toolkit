from concurrent import futures
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from backend.database_models.agent import Agent
from backend.services.logger import get_logger
from backend.tools.google_drive.actions import (
    create,
    delete,
    edit,
    move,
    permission_change,
    rename,
    restore,
)
from backend.tools.google_drive.auth import GoogleDriveAuth
from backend.tools.google_drive.constants import (
    ACTIVITY_TRACKING_WINDOW,
    SEARCH_MIME_TYPES,
    GoogleDriveActions,
)
from backend.tools.google_drive.tool import GoogleDrive
from backend.tools.google_drive.utils import get_current_timestamp_in_ms, get_service

logger = get_logger()


def handle_google_drive_activity_event(
    event_type: str, activity: Dict[str, str], agent_id: str, user_id: str, **kwargs
):
    index_name = "{}_{}".format(agent_id if agent_id is not None else user_id, GoogleDrive.NAME)
    (file_ids, titles) = (_extract_file_ids_from_target(activity=activity)[key] for key in ("file_ids", "titles"))
    if not file_ids:
        return

    match event_type:
        case GoogleDriveActions.CREATE.value:
            [
                create.apply_async(
                    args=[file_id, index_name, user_id],
                    kwargs=kwargs,
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.EDIT.value:
            [
                edit.apply_async(
                    args=[file_id, index_name, user_id],
                    kwargs=kwargs,
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.MOVE.value:
            [
                move.apply_async(
                    args=[file_id, index_name, user_id],
                    kwargs={
                        "title": titles[file_id],
                        "artifact_id": kwargs["artifact_id"],
                    },
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.RENAME.value:
            [
                rename.apply_async(
                    args=[file_id, index_name, user_id],
                    kwargs={
                        "title": titles[file_id],
                    },
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.DELETE.value:
            [
                delete.apply_async(
                    args=[file_id, index_name, user_id],
                    kwargs={
                        "title": titles[file_id],
                    },
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.RESTORE.value:
            [
                restore.apply_async(
                    args=[file_id, index_name, user_id],
                    kwargs=kwargs,
                )
                for file_id in file_ids
            ]
        case GoogleDriveActions.PERMISSION_CHANGE.value:
            [
                permission_change.apply_async(
                    args=[file_id, index_name, user_id],
                    kwargs=kwargs,
                )
                for file_id in file_ids
            ]
        case _:
            raise Exception("This action is not tracked for Google Drive")


def query_google_drive_activity(session: Session, agent: Agent, agent_artifacts: List[Dict[str, str]]):
    user_id = agent.user_id
    gdrive_auth = GoogleDriveAuth()
    agent_creator_auth_token = gdrive_auth.get_token(session=session, user_id=user_id)
    if agent_creator_auth_token is None:
        raise Exception("Sync GDrive Error: No agent creator credentials found")

    if gdrive_auth.is_auth_required(session, user_id=user_id):
        raise Exception("Sync GDrive Error: Agent creator credentials need to re-authenticate")

    (service,) = (get_service(api="driveactivity", version="v2", user_id=user_id)[key] for key in ("service",))

    activity_ts_filter = get_current_timestamp_in_ms(negative_offset=ACTIVITY_TRACKING_WINDOW)
    activities = []
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures_list = [
            executor.submit(_get_activity, service, artifact, activity_ts_filter) for artifact in agent_artifacts
        ]
        for future in futures.as_completed(futures_list):
            try:
                activities.append(future.result())
            except Exception as e:
                raise e

    return {agent_artifacts[index]["id"]: activities[index] for index in range(len(activities))}


def _get_activity(
    service: Any,
    artifact: Dict[str, str],
    activity_ts_filter: int,
    next_page_token: str = "",
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
                **({"ancestorName": "items/{}".format(artifact_id)} if artifact_type == "folder" else {}),
                **({"itemName": "items/{}".format(artifact_id)} if artifact_type == "file" else {}),
                "pageToken": next_page_token,
                "consolidationStrategy": {
                    "legacy": {},
                },
            }
        )
        .execute()
    )
    if response_next_page_token := response.get("nextPageToken", None):
        return [
            *response.get("activities", []),
            *_get_activity(
                service=service,
                artifact=artifact,
                activity_ts_filter=activity_ts_filter,
                next_page_token=response_next_page_token,
            ),
        ]
    return response["activities"] if response else []


def _extract_file_ids_from_target(activity: Dict[str, str]):
    file_ids = set()
    titles = {}
    targets = activity["targets"]
    for target in targets:
        # NOTE: if not a drive item then skip
        if driveItem := target["driveItem"]:
            mimeType = driveItem["mimeType"]
            # NOTE: if mime type not being tracked then skip
            if mimeType in SEARCH_MIME_TYPES:
                file_id = driveItem["name"].split("/")[1]
                file_ids.add(file_id)
                title = driveItem["title"]
                titles[file_id] = title
    return {"file_ids": file_ids, "titles": titles}
