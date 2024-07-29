from backend.services.logger import get_logger
from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT, Status
from backend.services.sync.env import env
from backend.tools.google_drive.actions.create import create

logger = get_logger()

ACTION_NAME = "restore"


@app.task(time_limit=DEFAULT_TIME_OUT)
def restore(file_id: str, index_name: str, user_id: str, **kwargs):
    return create(file_id=file_id, index_name=index_name, user_id=user_id, **kwargs)
