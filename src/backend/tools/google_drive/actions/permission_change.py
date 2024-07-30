import time

from backend.services.logger import get_logger
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env

logger = get_logger()

ACTION_NAME = "permission_change"


@app.task(time_limit=DEFAULT_TIME_OUT)
def permission_change(file_id: str, index_name: str, user_id: str, **kwargs):
    logger.info(
        "Initiating Compass create_index action for index {}".format(index_name)
    )
    env().COMPASS.invoke(
        env().COMPASS.ValidActions.CREATE_INDEX,
        {
            "index": index_name,
        },
    )
    logger.info("Finished Compass create_index action for index {}".format(index_name))
    logger.info("Initiating Compass add_context action for file {}".format(file_id))
    env().COMPASS.invoke(
        env().COMPASS.ValidActions.ADD_CONTEXT,
        {
            "index": index_name,
            "file_id": file_id,
            "context": {
                "last_updated": int(time.time()),
                "permissions": [],
            },
        },
    )
    logger.info("Finished Compass add_context action for file {}".format(file_id))
    return {"action": ACTION_NAME, "status": Status.SUCCESS.value, "file_id": file_id}
