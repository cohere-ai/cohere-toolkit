from backend.services.logger.utils import logger
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env

ACTION_NAME = "delete"


@app.task(time_limit=DEFAULT_TIME_OUT)
def delete(file_id: str, index_name: str, user_id: str, **kwargs):
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
    logger.info("Initiating Compass delete for file {}".format(file_id))
    env().COMPASS.invoke(
        env().COMPASS.ValidActions.DELETE,
        {
            "index": index_name,
            "file_id": file_id,
        },
    )
    logger.info("Finished Compass delete action for file {}".format(file_id))
    return {
        "action": ACTION_NAME,
        "status": Status.SUCCESS.value,
        "file_id": file_id,
    }
