from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base, MinimalBase


class SyncCeleryTaskMeta(MinimalBase):
    __tablename__ = "sync_celery_taskmeta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[str] = mapped_column(String(155), unique=True)
    status: Mapped[str] = mapped_column(String(50))
    result: Mapped[bytes] = mapped_column(LargeBinary)
    date_done: Mapped[DateTime] = mapped_column(DateTime)
    traceback: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(String(155))
    args: Mapped[bytes] = mapped_column(LargeBinary)
    kwargs: Mapped[bytes] = mapped_column(LargeBinary)
    worker: Mapped[str] = mapped_column(String(155))
    retries: Mapped[int] = mapped_column(Integer)
    queue: Mapped[str] = mapped_column(String(155))


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    agent_id: Mapped[str] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )

    task_id: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("agent_id", "task_id", name="unique_agent_task"),
    )
