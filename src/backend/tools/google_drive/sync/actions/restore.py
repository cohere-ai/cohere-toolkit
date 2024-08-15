from backend.services.sync import app
from backend.services.sync.constants import DEFAULT_TIME_OUT
from backend.tools.google_drive.sync.actions.create import create

ACTION_NAME = "restore"


@app.task(time_limit=DEFAULT_TIME_OUT)
def restore(file_id: str, index_name: str, user_id: str, agent_id: str, **kwargs):
    response = create(
        file_id=file_id,
        index_name=index_name,
        user_id=user_id,
        agent_id=agent_id,
        **kwargs
    )
    response["action"] = ACTION_NAME
    return response
