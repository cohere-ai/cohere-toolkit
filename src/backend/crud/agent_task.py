from backend.database_models.agent_task import AgentTask, SyncCeleryTaskMeta
from backend.services.transaction import validate_transaction
from sqlalchemy.orm import Session
from typing import List

@validate_transaction
def create_agent_task(db: Session, agent_id: str, task_id: str) -> AgentTask:
  db.add(AgentTask(agent_id=agent_id, task_id=task_id))
  db.commit()
  db.refresh(AgentTask)
  return blacklist

@validate_transaction
def get_agent_tasks_by_agent_id(db: Session, agent_id: str) -> List[SyncCeleryTaskMeta]:
    return (db.query(SyncCeleryTaskMeta)
              .join(AgentTask, AgentTask.task_id == SyncCeleryTaskMeta.task_id)
              .filter(AgentTask.agent_id == agent_id)
              .all())
