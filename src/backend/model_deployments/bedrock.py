import os
from typing import Any, Dict, Generator, List

import cohere
from cohere.types import StreamedChatResponse

from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest

BEDROCK_ACCESS_KEY_ENV_VAR = "BEDROCK_ACCESS_KEY"
BEDROCK_SECRET_KEY_ENV_VAR = "BEDROCK_SECRET_KEY"
BEDROCK_SESSION_TOKEN_ENV_VAR = "BEDROCK_SESSION_TOKEN"
BEDROCK_REGION_NAME_ENV_VAR = "BEDROCK_REGION_NAME"
BEDROCK_ENV_VARS = [
    BEDROCK_ACCESS_KEY_ENV_VAR,
    BEDROCK_SECRET_KEY_ENV_VAR,
    BEDROCK_SESSION_TOKEN_ENV_VAR,
    BEDROCK_REGION_NAME_ENV_VAR,
]


class BedrockDeployment(BaseDeployment):
    DEFAULT_MODELS = ["cohere.command-r-plus-v1:0"]

    def __init__(self, **kwargs: Any):
        self.client = cohere.BedrockClient(
            # TODO: remove hardcoded models once the SDK is updated
            chat_model="cohere.command-r-plus-v1:0",
            embed_model="cohere.embed-multilingual-v3",
            generate_model="cohere.command-text-v14",
            aws_access_key=get_model_config_var(BEDROCK_ACCESS_KEY_ENV_VAR, **kwargs),
            aws_secret_key=get_model_config_var(BEDROCK_SECRET_KEY_ENV_VAR, **kwargs),
            aws_session_token=get_model_config_var(
                BEDROCK_SESSION_TOKEN_ENV_VAR, **kwargs
            ),
            aws_region=get_model_config_var(BEDROCK_REGION_NAME_ENV_VAR, **kwargs),
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
        return all([os.environ.get(var) is not None for var in BEDROCK_ENV_VARS])

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
