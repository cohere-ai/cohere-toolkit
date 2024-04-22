from typing import Any, Dict, Generator, List

from cohere.types import StreamedChatResponse

from backend.chat.custom.model_deployments.base import BaseDeployment
from backend.chat.enums import StreamEvent
from backend.schemas.cohere_chat import CohereChatRequest


class MockCohereDeployment(BaseDeployment):
    """Mocked Cohere Platform Deployment."""

    DEFAULT_MODELS = ["command", "command-r"]

    @property
    def rerank_enabled(self) -> bool:
        return True

    @classmethod
    def list_models(cls) -> List[str]:
        return cls.DEFAULT_MODELS

    @classmethod
    def is_available(cls) -> bool:
        return True

    def invoke_chat(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
        return {
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

    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        events = [
            {
                "event_type": StreamEvent.STREAM_START,
                "generation_id": "test",
                "is_finished": False,
            },
            {
                "event_type": StreamEvent.TEXT_GENERATION,
                "text": "This is a test.",
                "is_finished": True,
            },
            {
                "event_type": StreamEvent.STREAM_END,
                "is_finished": True,
                "generation_id": "test",
                "citations": [],
                "documents": [],
                "search_results": [],
                "search_queries": [],
                "finish_reason": "MAX_TOKENS",
            },
        ]

        for event in events:
            yield event

    def invoke_search_queries(
        self,
        message: str,
        chat_history: List[Dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> list[str]:
        # TODO: Add
        pass

    def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        # TODO: Add
        pass

    def invoke_tools(self, message: str, tools: List[Any], **kwargs: Any) -> List[Any]:
        # TODO: Add
        pass
