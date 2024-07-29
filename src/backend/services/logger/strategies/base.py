from abc import abstractmethod
from typing import Any

from src.backend.schemas.context import Context


class BaseLogger:
    """Base for all logger options."""

    @abstractmethod
    def setup(self, ctx: Context, **kwargs: Any) -> Any: ...

    @abstractmethod
    def info(self, msg: str | None, **kwargs: Any) -> Any: ...

    @abstractmethod
    def error(self, msg: str | None, **kwargs: Any) -> Any: ...

    @abstractmethod
    def warning(self, msg: str | None, **kwargs: Any) -> Any: ...

    @abstractmethod
    def debug(self, msg: str | None, **kwargs: Any) -> Any: ...

    @abstractmethod
    def critical(self, msg: str | None, **kwargs: Any) -> Any: ...

    @abstractmethod
    def exception(self, msg: str | None, **kwargs: Any) -> Any: ...
