from backend.services.logger import get_logger
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env
from backend.tools.google_drive.actions.utils import get_folder_subfolders
from backend.tools.google_drive.utils import get_service

logger = get_logger()

ACTION_NAME = "move"


@app.task(time_limit=DEFAULT_TIME_OUT)
def move(file_id: str, index_name: str, user_id: str, **kwargs):
    title = kwargs["title"]
    artifact_id = kwargs["artifact_id"]
    # folder_subfolders = get_folder_subfolders(folder_id=artifact_id, user_id=user_id)
    folder_subfolders = []

    (service,) = (get_service(api="drive", user_id=user_id)[key] for key in ("service",))

    folders_query = " or ".join(
        ["'{}' in parents".format(folder_id) for folder_id in [artifact_id, *folder_subfolders]]
    )
    response = (
        service.files()
        .list(
            q="({}) and name = '{}'".format(folders_query, title),
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        )
        .execute()
    )

    delete = True
    if files := response.get("files", None):
        found_file = [x for x in files if x["id"] == file_id]
        if found_file:
            delete = False

    # Delete file if moved out of agent's artifacts
    if delete:
        logger.info("Initiating Compass move action for file_id {}".format(file_id))
        # Delete document
        env().COMPASS.invoke(
            env().COMPASS.ValidActions.DELETE,
            {
                "index": index_name,
                "file_id": file_id,
            },
        )
        logger.info("Finished Compass move action for file_id {}".format(file_id))
        return {
            "action": ACTION_NAME,
            "status": Status.SUCCESS.value,
            "file_id": file_id,
        }

    return {"action": ACTION_NAME, "status": Status.CANCELLED.value, "file_id": file_id}
