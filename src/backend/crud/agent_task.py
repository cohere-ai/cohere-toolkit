from typing import List

from sqlalchemy.orm import Session

from backend.database_models.agent_task import AgentTask, SyncCeleryTaskMeta
from backend.services.logger.utils import LoggerFactory
from backend.services.transaction import validate_transaction

logger = LoggerFactory().get_logger()


@validate_transaction
def create_agent_task(db: Session, agent_id: str, task_id: str) -> AgentTask:
    agent_task = AgentTask(agent_id=agent_id, task_id=task_id)
    db.add(agent_task)
    db.commit()
    db.refresh(agent_task)
    return agent_task


# TODO: clean up
@validate_transaction
def get_agent_tasks_by_agent_id(db: Session, agent_id: str) -> List[SyncCeleryTaskMeta]:
    return (
        db.query(SyncCeleryTaskMeta)
        .join(AgentTask, AgentTask.task_id == SyncCeleryTaskMeta.task_id)
        .filter(AgentTask.agent_id == agent_id)
        .all()
    )
