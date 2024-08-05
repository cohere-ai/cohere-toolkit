from abc import abstractmethod
from typing import Any


class BaseLogger:
    """Base for all logger options."""

    @abstractmethod
    def setup(self, ctx: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def info(self, **kwargs: Any) -> Any: ...

    @abstractmethod
    def error(self, **kwargs: Any) -> Any: ...

    @abstractmethod
    def warning(self, **kwargs: Any) -> Any: ...

    @abstractmethod
    def debug(self, **kwargs: Any) -> Any: ...

    @abstractmethod
    def critical(self, **kwargs: Any) -> Any: ...

    @abstractmethod
    def exception(self, **kwargs: Any) -> Any: ...
