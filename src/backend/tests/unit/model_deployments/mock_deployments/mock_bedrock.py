from typing import Any, Generator

from cohere.types import StreamedChatResponse

from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from backend.tests.unit.model_deployments.mock_deployments.mock_base import (
    MockDeployment,
)


class MockBedrockDeployment(MockDeployment):
    """Bedrock Deployment"""

    DEFAULT_MODELS = ["cohere.command-r-plus-v1:0"]

    def __init__(self, **kwargs: Any):
        pass

    @staticmethod
    def name() -> str:
        return "Bedrock"

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
        event = {
            "text": "Hi! Hello there! How's it going?",
            "generation_id": "ca0f398e-f8c8-48f0-b093-12d1754d00ed",
            "citations": None,
            "documents": None,
            "is_search_required": None,
            "search_queries": None,
            "search_results": None,
            "finish_reason": "MAX_TOKENS",
            "tool_calls": None,
            "chat_history": [
                {"role": "USER", "message": "Hello"},
                {"role": "CHATBOT", "message": "Hi! Hello there! How's it going?"},
            ],
            "response_id": "7f2c0ab4-e0d0-4808-891e-d5c6362e407a",
            "meta": {
                "api_version": {"version": "1"},
                "billed_units": {"input_tokens": 1, "output_tokens": 10},
                "tokens": {"input_tokens": 67, "output_tokens": 10},
            },
        }
        yield event

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
MockBedrockDeployment.__name__ = "BedrockDeployment"
