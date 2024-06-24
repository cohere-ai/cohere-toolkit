from sqlalchemy import DateTime, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database_models.base import Base


class ToolAuth(Base):
    __tablename__ = "tool_auth"

    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    tool_id: Mapped[str] = mapped_column(Text, nullable=False)
    token_type: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_access_token: Mapped[bytes] = mapped_column()
    encrypted_refresh_token: Mapped[bytes] = mapped_column()
    expires_at = mapped_column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "tool_id", name="_user_tool_uc"),)
