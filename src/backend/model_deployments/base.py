from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List

from backend.config.settings import Settings
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from backend.schemas.deployment import DeploymentInfo


class BaseDeployment(ABC):
    """Base for all model deployment options.

    rerank_enabled: bool: Whether the deployment supports reranking.
    invoke_chat_stream: Generator[StreamedChatResponse, None, None]: Invoke the chat stream.
    invoke_rerank: Any: Invoke the rerank.
    list_models: List[str]: List all models.
    is_available: bool: Check if the deployment is available.
    """
    @classmethod
    def id(cls) -> str:
        return cls.name().replace(" ", "_").lower()

    @classmethod
    @abstractmethod
    def name(cls) -> str: ...

    @classmethod
    @abstractmethod
    def env_vars(cls) -> List[str]: ...

    @classmethod
    @abstractmethod
    def rerank_enabled(cls) -> bool: ...

    @classmethod
    @abstractmethod
    def list_models(cls) -> List[str]: ...

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool: ...

    @classmethod
    def is_community(cls) -> bool:
        return False

    @classmethod
    def config(cls) -> Dict[str, Any]:
        config = Settings().safe_lookup("deployments", cls.id(), default={})
        return config.dict() if config else {}

    @classmethod
    def to_deployment_info(cls) -> DeploymentInfo:
        data = {
            "id": cls.id(),
            "name": cls.name(),
            "description": None,
            "models": cls.list_models(),
            "is_community": cls.is_community(),
            "is_available": cls.is_available(),
            "config": cls.config(),
        }
        return DeploymentInfo(**data)

    @abstractmethod
    async def invoke_chat(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Any: ...

    @abstractmethod
    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> AsyncGenerator[Any, Any]: ...

    @abstractmethod
    async def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], ctx: Context, **kwargs: Any
    ) -> Any: ...
