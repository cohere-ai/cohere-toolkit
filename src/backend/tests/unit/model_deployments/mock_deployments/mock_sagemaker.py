from typing import Any, Generator

from cohere.types import StreamedChatResponse

from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from backend.tests.unit.model_deployments.mock_deployments.mock_base import (
    MockDeployment,
)


class MockSageMakerDeployment(MockDeployment):
    """SageMaker Deployment"""

    DEFAULT_MODELS = ["command-r"]

    def __init__(self, **kwargs: Any):
        pass

    @staticmethod
    def name() -> str:
        return "SageMaker"

    @staticmethod
    def env_vars() -> list[str]:
        return []

    @staticmethod
    def rerank_enabled() -> bool:
        return False

    @classmethod
    def list_models(cls) -> list[str]:
        return cls.DEFAULT_MODELS

    @staticmethod
    def is_available() -> bool:
        return False

    async def invoke_chat(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        pass

    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        for event in self.event_stream:
            yield event

    async def invoke_rerank(
        self, query: str, documents: list[str], ctx: Context, **kwargs: Any

    ) -> Any:
        return None

# Overriding the name so that the proper deployment is selected
MockSageMakerDeployment.__name__ = "SageMakerDeployment"
