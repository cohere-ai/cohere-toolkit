import os
from typing import Any, Dict, Generator, List

import cohere
from cohere.types import StreamedChatResponse

from backend.model_deployments.base import BaseDeployment
from backend.schemas.cohere_chat import CohereChatRequest


class BedrockDeployment(BaseDeployment):
    DEFAULT_MODELS = ["cohere.command-r-plus-v1:0"]
    access_key = os.environ.get("BEDROCK_ACCESS_KEY")
    secret_key = os.environ.get("BEDROCK_SECRET_KEY")
    session_token = os.environ.get("BEDROCK_SESSION_TOKEN")
    region_name = os.environ.get("BEDROCK_REGION_NAME")

    def __init__(self):
        self.client = cohere.BedrockClient(
            # TODO: remove hardcoded models once the SDK is updated
            chat_model="cohere.command-r-plus-v1:0",
            embed_model="cohere.embed-multilingual-v3",
            generate_model="cohere.command-text-v14",
            aws_access_key=self.access_key,
            aws_secret_key=self.secret_key,
            aws_session_token=self.session_token,
            aws_region=self.region_name,
        )

    @property
    def rerank_enabled(self) -> bool:
        return False

    @classmethod
    def list_models(cls) -> List[str]:
        if not cls.is_available():
            return []

        return cls.DEFAULT_MODELS

    @classmethod
    def is_available(cls) -> bool:
        return all(
            [
                cls.access_key is not None,
                cls.secret_key is not None,
                cls.session_token is not None,
                cls.region_name is not None,
            ]
        )

    def invoke_chat(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
        # bedrock accepts a subset of the chat request fields
        bedrock_chat_req = chat_request.model_dump(
            exclude={"tools", "conversation_id", "model", "stream"}, exclude_none=True
        )

        return self.client.chat(
            **bedrock_chat_req,
            **kwargs,
        )

    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        # bedrock accepts a subset of the chat request fields
        bedrock_chat_req = chat_request.model_dump(
            exclude={"tools", "conversation_id", "model", "stream"}, exclude_none=True
        )

        stream = self.client.chat_stream(
            **bedrock_chat_req,
            **kwargs,
        )
        for event in stream:
            yield event.__dict__

    def invoke_search_queries(
        self,
        message: str,
        chat_history: List[Dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> list[str]:
        res = self.client.chat(
            message=message,
            chat_history=chat_history,
            search_queries_only=True,
            **kwargs,
        )

        if not res.search_queries:
            return []

        return [s.text for s in res.search_queries]

    def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        return None

    def invoke_tools(self, message: str, tools: List[Any], **kwargs: Any) -> List[Any]:
        return None
