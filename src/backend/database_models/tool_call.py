from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class ToolCall(Base):
    """
    Default ToolCall model for tool calls.
    """

    __tablename__ = "tool_calls"

    name: Mapped[str]
    parameters: Mapped[dict] = mapped_column(JSON, nullable=True)
    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )

    __table_args__ = (Index("tool_call_message_id", message_id),)
