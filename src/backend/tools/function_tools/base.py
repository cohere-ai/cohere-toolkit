from abc import abstractmethod
from typing import Any, Dict, List


class BaseFunctionTool:
    """Base for all retrieval options."""

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool: ...

    @abstractmethod
    def call(self, parameters: str, **kwargs: Any) -> List[Dict[str, Any]]: ...
