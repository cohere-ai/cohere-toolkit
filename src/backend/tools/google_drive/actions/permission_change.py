import time

from backend.services.logger.utils import logger
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env
from backend.tools.google_drive.actions.utils import list_permissions

ACTION_NAME = "permission_change"


@app.task(time_limit=DEFAULT_TIME_OUT)
def permission_change(file_id: str, index_name: str, user_id: str, **kwargs):
    permissions = list_permissions(file_id=file_id, user_id=user_id)
    # Update permissions array
    logger.info(
        event="[Google Drive Permission Change] Initiating Compass add_context action for file",
        file_id=file_id,
    )
    env().COMPASS.invoke(
        env().COMPASS.ValidActions.ADD_CONTEXT,
        {
            "index": index_name,
            "file_id": file_id,
            "context": {
                "last_updated": int(time.time()),
                "permissions": permissions,
            },
        },
    )
    logger.info(
        event="[Google Drive Permission Change] Finished Compass add_context action for file",
        file_id=file_id,
    )
    return {"action": ACTION_NAME, "status": Status.SUCCESS.value, "file_id": file_id}
