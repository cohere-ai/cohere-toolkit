from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, mapped_column


class Base(DeclarativeBase):
    id = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    created_at = mapped_column(
        DateTime,
        default=func.now(),
    )

    updated_at = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
    )
