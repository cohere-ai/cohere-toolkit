from concurrent import futures
from typing import Any, Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from backend.database_models.agent import Agent
from backend.services.logger import get_logger

from .actions import create
from .auth import GoogleDriveAuth
from .constants import ACTIVITY_TRACKING_WINDOW, SEARCH_MIME_TYPES, GoogleDriveActions
from .tool import GoogleDrive
from .utils import get_current_timestamp_in_ms

logger = get_logger()


def handle_google_drive_activity_event(event_type: str, activity: Dict[str, str], agent_id: str, user_id: str):
    index_name = "{}_{}".format(agent_id if agent_id is not None else user_id, GoogleDrive.NAME)
    match event_type:
        case GoogleDriveActions.CREATE.value:
            file_ids = set()
            targets = activity["targets"]
            for target in targets:
                # NOTE: if not a drive item then skip
                if driveItem := target["driveItem"]:
                    mimeType = driveItem["mimeType"]
                    # NOTE: if mime type not being tracked then skip
                    if mimeType in SEARCH_MIME_TYPES:
                        file_id = driveItem["name"].split("/")[1]
                        file_ids.add(file_id)
            if file_ids:
                [
                    create.apply_async(
                        args=[event_type, file_id, index_name],
                        kwargs={"user_id": user_id},
                    )
                    for file_id in file_ids
                ]
        case GoogleDriveActions.EDIT.value:
            print("edit")
        case GoogleDriveActions.MOVE.value:
            print("move")
        case GoogleDriveActions.RENAME.value:
            print("rename")
        case GoogleDriveActions.DELETE.value:
            print("delete")
        case GoogleDriveActions.RESTORE.value:
            print("restore")
        case GoogleDriveActions.PERMISSION_CHANGE.value:
            print("permission_change")
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

    creds = Credentials(agent_creator_auth_token)
    service = build("driveactivity", "v2", credentials=creds, cache_discovery=False)

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
            *response["activities"],
            *_get_activity(
                service=service,
                artifact=artifact,
                activity_ts_filter=activity_ts_filter,
                next_page_token=response_next_page_token,
            ),
        ]
    return response["activities"] if response else []
