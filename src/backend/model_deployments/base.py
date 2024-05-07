from abc import abstractmethod
from typing import Any, Dict, Generator, List

from cohere.types import StreamedChatResponse

from backend.schemas.cohere_chat import CohereChatRequest


class BaseDeployment:
    """Base for all model deployment options.

    rerank_enabled: bool: Whether the deployment supports reranking.
    invoke_chat_stream: Generator[StreamedChatResponse, None, None]: Invoke the chat stream.
    invoke_search_queries: list[str]: Invoke the search queries.
    invoke_rerank: Any: Invoke the rerank.
    invoke_tools: Any: Invoke the tools.
    list_models: List[str]: List all models.
    is_available: bool: Check if the deployment is available.
    """

    @property
    @abstractmethod
    def rerank_enabled(self) -> bool: ...

    @abstractmethod
    def invoke_chat(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any: ...

    @abstractmethod
    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]: ...

    @abstractmethod
    def invoke_search_queries(
        self,
        message: str,
        chat_history: List[Dict[str, str]] | None = None,
        **kwargs: Any
    ) -> list[str]: ...

    @abstractmethod
    def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], **kwargs: Any
    ) -> Any: ...

    @abstractmethod
    def invoke_tools(self, message: str, tools: List[Any], **kwargs: Any) -> Any: ...

    @staticmethod
    def list_models() -> List[str]: ...

    @staticmethod
    def is_available() -> bool: ...
