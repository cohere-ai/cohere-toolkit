# make sure to upsert the agent task
from typing import Any, List
from sqlalchemy.orm import Session
from backend.database_models.blacklist import Blacklist
from backend.services.transaction import validate_transaction


@validate_transaction
def create_agent_task(db: Session, agent_id: str, task_id: str):
    """
    Create a new agent task.
    """
    # TODO: add this to agent_tasks table and not blacklist obviously
    blacklist = Blacklist(token_id=f"agent:{agent_id}-task:{task_id}")
    db.add(blacklist)
    db.commit()
    db.refresh(blacklist)


def list_agent_tasks(db: Session, agent_task_id: str) -> List[Any]:
    """
    Get an agent task by its ID.
    """
    pass
