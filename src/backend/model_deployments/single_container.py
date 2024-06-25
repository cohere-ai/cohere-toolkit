import os
from typing import Any, Dict, Generator, List

import cohere
from cohere.types import StreamedChatResponse

from backend.chat.collate import to_dict
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest
from backend.services.metrics import (
    collect_metrics_chat,
    collect_metrics_chat_stream,
    collect_metrics_rerank,
)

DEFAULT_RERANK_MODEL = "rerank-english-v2.0"
SC_URL_ENV_VAR = "SINGLE_CONTAINER_URL"
SC_MODEL_ENV_VAR = "SINGLE_CONTAINER_MODEL"
SC_ENV_VARS = [SC_URL_ENV_VAR, SC_MODEL_ENV_VAR]


class SingleContainerDeployment(BaseDeployment):
    """Single Container Deployment."""

    client_name = "cohere-toolkit"

    def __init__(self, **kwargs: Any):
        self.url = get_model_config_var(SC_URL_ENV_VAR, **kwargs)
        self.model = get_model_config_var(SC_MODEL_ENV_VAR, **kwargs)
        self.client = cohere.Client(
            base_url=self.url, client_name=self.client_name, api_key="none"
        )

    @property
    def rerank_enabled(self) -> bool:
        return os.environ.get(SC_MODEL_ENV_VAR).startswith("rerank")

    @classmethod
    def list_models(cls) -> List[str]:
        if not SingleContainerDeployment.is_available():
            return []

        return [os.environ.get(SC_MODEL_ENV_VAR)]

    @classmethod
    def is_available(cls) -> bool:
        return all([os.environ.get(var) is not None for var in SC_ENV_VARS])

    @collect_metrics_chat
    def invoke_chat(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
        response = self.client.chat(
            **chat_request.model_dump(exclude={"stream", "file_ids", "model"}),
            **kwargs,
        )
        yield to_dict(response)

    @collect_metrics_chat_stream
    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        stream = self.client.chat_stream(
            **chat_request.model_dump(exclude={"stream", "file_ids", "model"}),
            **kwargs,
        )

        for event in stream:
            yield to_dict(event)

    @collect_metrics_rerank
    def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        return self.client.rerank(
            query=query, documents=documents, model=DEFAULT_RERANK_MODEL, **kwargs
        )
