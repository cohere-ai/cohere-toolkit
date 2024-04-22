from abc import abstractmethod
from typing import Any, Dict, List


class BaseRetrieval:
    """Base for all retrieval options."""

    @abstractmethod
    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]: ...

    def validate_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Validate the documents retrieved. A valid document should have a text field."""
        for document in documents:
            if "text" not in document:
                return False
        return True
