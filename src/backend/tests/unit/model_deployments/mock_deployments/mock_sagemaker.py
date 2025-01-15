from typing import Any, Generator

from cohere.types import StreamedChatResponse

from backend.chat.enums import StreamEvent
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
        return True

    def invoke_chat(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        pass

    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        events = [
            {
                "event_type": StreamEvent.STREAM_START,
                "generation_id": "test",
            },
            {
                "event_type": StreamEvent.TEXT_GENERATION,
                "text": "This is a test.",
            },
            {
                "event_type": StreamEvent.STREAM_END,
                "response": {
                    "generation_id": "test",
                    "citations": [],
                    "documents": [],
                    "search_results": [],
                    "search_queries": [],
                },
                "finish_reason": "MAX_TOKENS",
            },
        ]

        for event in events:
            yield event

    def invoke_rerank(
        self, query: str, documents: list[str], ctx: Context, **kwargs: Any
    ) -> Any:
        return None
