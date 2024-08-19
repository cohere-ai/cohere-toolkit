from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status

from .utils import init_compass, persist_agent_task

ACTION_NAME = "delete"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT, bind=True)
@persist_agent_task
def delete(self, file_id: str, index_name: str, user_id: str, agent_id: str, **kwargs):
    compass = init_compass()

    try:
        # Delete document
        logger.info(
            event="[Google Drive Delete] Initiating Compass delete for file",
            file_id=file_id,
        )
        compass.invoke(
            compass.ValidActions.DELETE,
            {
                "index": index_name,
                "file_id": file_id,
            },
        )
        logger.info(
            event="[Google Drive Delete] Finished Compass delete action for file",
            file_id=file_id,
        )
        return {
            "action": ACTION_NAME,
            "status": Status.SUCCESS.value,
            "file_id": file_id,
        }
    except Exception as error:
        logger.error(
            event="Failed to delete document in Compass for file",
            user_id=user_id,
            agent_id=agent_id,
            index_name=index_name,
            file_id=file_id,
        )
        err_msg = (
            f"Error deleting file {file_id} for agent {agent_id} on Compass: {error}"
        )
        raise Exception(err_msg)
