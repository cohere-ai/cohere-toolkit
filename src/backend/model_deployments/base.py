from abc import ABC, abstractmethod
from typing import Any

from backend.config.settings import Settings
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from backend.schemas.deployment import DeploymentDefinition


class BaseDeployment(ABC):
    """Base for all model deployment options.

    rerank_enabled: bool: Whether the deployment supports reranking.
    invoke_chat_stream: Generator[StreamedChatResponse, None, None]: Invoke the chat stream.
    invoke_rerank: Any: Invoke the rerank.
    list_models: List[str]: List all models.
    is_available: bool: Check if the deployment is available.
    """
    db_id = None

    def __init__(self, db_id=None, **kwargs: Any):
        self.db_id = db_id

    @classmethod
    def id(cls) -> str:
        return cls.db_id if cls.db_id else cls.name().replace(" ", "_").lower()

    @staticmethod
    @abstractmethod
    def name() -> str: ...

    @staticmethod
    @abstractmethod
    def env_vars() -> list[str]: ...

    @staticmethod
    @abstractmethod
    def rerank_enabled() -> bool: ...

    @classmethod
    @abstractmethod
    def list_models(cls) -> list[str]: ...

    @staticmethod
    @abstractmethod
    def is_available() -> bool: ...

    @classmethod
    def is_community(cls) -> bool:
        return False

    @classmethod
    def config(cls) -> dict[str, Any]:
        config = Settings().get(f"deployments.{cls.id()}")
        config_dict = {} if not config else dict(config)
        for key, value in config_dict.items():
            if value is None:
                config_dict[key] = ""
        return config_dict

    @classmethod
    def to_deployment_definition(cls) -> DeploymentDefinition:
        return DeploymentDefinition(
            id=cls.id(),
            name=cls.name(),
            description=None,
            models=cls.list_models(),
            is_community=cls.is_community(),
            is_available=cls.is_available(),
            config=cls.config(),
            class_name=cls.__name__,
        )

    @abstractmethod
    async def invoke_chat(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Any: ...

    @abstractmethod
    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> Any: ...

    @abstractmethod
    async def invoke_rerank(
        self, query: str, documents: list[str], ctx: Context, **kwargs: Any
    ) -> Any: ...
