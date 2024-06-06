from abc import abstractmethod
from typing import Any, Dict, List


class BaseTool:
    """
    Abstract base class for all Tools.
    """

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool: ...

    @abstractmethod
    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]: ...
