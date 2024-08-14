from typing import Any, Dict, Generator, List

from cohere.types import StreamedChatResponse

from backend.chat.enums import StreamEvent
from backend.model_deployments.base import BaseDeployment
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context


class MockSageMakerDeployment(BaseDeployment):
    """SageMaker Deployment"""

    DEFAULT_MODELS = ["command-r"]

    @property
    def rerank_enabled(self) -> bool:
        return False

    @classmethod
    def list_models(cls) -> List[str]:
        return cls.DEFAULT_MODELS

    @classmethod
    def is_available(cls) -> bool:
        return True

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
        self, query: str, documents: List[Dict[str, Any]], ctx: Context, **kwargs: Any
    ) -> Any:
        return None
