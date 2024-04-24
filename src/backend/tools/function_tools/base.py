from abc import abstractmethod
from typing import Any, Dict, List


class BaseFunctionTool:
    """Base for all retrieval options."""

    @abstractmethod
    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]: ...
