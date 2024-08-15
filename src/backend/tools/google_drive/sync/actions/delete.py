from backend.config.settings import Settings
from backend.services.compass import Compass
from backend.services.logger.utils import LoggerFactory
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from .utils import persist_agent_task

ACTION_NAME = "delete"
logger = LoggerFactory().get_logger()


@app.task(time_limit=DEFAULT_TIME_OUT, bind=True)
@persist_agent_task
def delete(file_id: str, index_name: str, user_id: str, agent_id: str, **kwargs):
    compass = Compass(
        compass_api_url=Settings().compass.api_url,
        compass_parser_url=Settings().compass.parser_url,
        compass_username=Settings().compass.username,
        compass_password=Settings().compass.password,
    )

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
            event="Failed to create document in Compass for file",
            web_view_link=file_id,
        )
        return {
            "action": ACTION_NAME,
            "status": Status.FAIL.value,
            "file_id": file_id,
            "message": str(error),
        }
