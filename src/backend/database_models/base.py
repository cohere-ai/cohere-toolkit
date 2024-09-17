from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Query, mapped_column


class FilterFields(StrEnum):
    ORGANIZATION_ID = "organization_id"


class CustomFilterQuery(Query):
    """
    Custom query class that filters by field if the entity has field
    and the filter value is set.
    """

    ALLOWED_FILTER_FIELDS = [FilterFields.ORGANIZATION_ID]

    def __new__(cls, *args, **kwargs):
        from backend.services.context import GLOBAL_REQUEST_CONTEXT

        request_ctx = GLOBAL_REQUEST_CONTEXT.get()
        if request_ctx and request_ctx.use_global_filtering:
            query = None
            for field in cls.ALLOWED_FILTER_FIELDS:
                if (
                    args
                    and hasattr(args[0][0], field)
                    and hasattr(request_ctx, field)
                    and getattr(request_ctx, field)
                ):
                    if query:
                        query = query.filter_by(**{field: getattr(request_ctx, field)})
                    else:
                        query = Query(*args, **kwargs).filter_by(
                            **{field: getattr(request_ctx, field)}
                        )
            if query:
                return query

        return object.__new__(cls)


class MinimalBase(DeclarativeBase):
    pass


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
