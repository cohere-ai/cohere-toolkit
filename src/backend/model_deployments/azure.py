import logging
import os
import threading
import time
from typing import Any, Dict, Generator, List

import cohere
from cohere.core.api_error import ApiError
from cohere.types import StreamedChatResponse

from backend.chat.collate import to_dict
from backend.chat.enums import StreamEvent
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest
from backend.services.metrics import (
    collect_metrics_chat,
    collect_metrics_chat_stream,
    collect_metrics_rerank,
)

AZURE_API_KEY_ENV_VAR = "AZURE_API_KEY"
# Example URL: "https://<endpoint>.<region>.inference.ai.azure.com/v1"
# Note: It must have /v1 and it should not have /chat
AZURE_CHAT_URL_ENV_VAR = "AZURE_CHAT_ENDPOINT_URL"
AZURE_ENV_VARS = [AZURE_API_KEY_ENV_VAR, AZURE_CHAT_URL_ENV_VAR]


class AzureDeployment(BaseDeployment):
    """
    Azure Deployment.
    How to deploy a model:
    https://learn.microsoft.com/azure/ai-studio/how-to/deploy-models-cohere-command
    """

    DEFAULT_MODELS = ["azure-command"]

    def __init__(self, **kwargs: Any):
        # Override the environment variable from the request
        self.api_key = get_model_config_var(AZURE_API_KEY_ENV_VAR, **kwargs)
        self.chat_endpoint_url = get_model_config_var(AZURE_CHAT_URL_ENV_VAR, **kwargs)

        if not self.chat_endpoint_url.endswith("/v1"):
            self.chat_endpoint_url = self.chat_endpoint_url + "/v1"
        print("Azure chat endpoint url: ", self.chat_endpoint_url)
        self.client = cohere.Client(
            base_url=self.chat_endpoint_url, api_key=self.api_key
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
        return all([os.environ.get(var) is not None for var in AZURE_ENV_VARS])

    @collect_metrics_chat
    def invoke_chat(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
        response = self.client.chat(
            **chat_request.model_dump(exclude={"stream", "file_ids"}),
            **kwargs,
        )
        yield to_dict(response)

    @collect_metrics_chat_stream
    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        stream = self.client.chat_stream(
            **chat_request.model_dump(exclude={"stream", "file_ids"}),
            **kwargs,
        )

        for event in stream:
            yield to_dict(event)

    def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        return None
