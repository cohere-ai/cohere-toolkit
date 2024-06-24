import asyncio
import logging
import os
import threading
import time
from typing import Any, Dict, Generator, List

import cohere
import requests
from cohere.core.api_error import ApiError
from cohere.types import StreamedChatResponse

from backend.chat.collate import to_dict
from backend.chat.enums import StreamEvent
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.metrics import MetricsData
from backend.services.metrics import (
    collect_metrics_chat,
    collect_metrics_chat_stream,
    collect_metrics_rerank,
)

COHERE_API_KEY_ENV_VAR = "COHERE_API_KEY"
COHERE_ENV_VARS = [COHERE_API_KEY_ENV_VAR]
DEFAULT_RERANK_MODEL = "rerank-english-v2.0"


class CohereDeployment(BaseDeployment):
    """Cohere Platform Deployment."""

    client_name = "cohere-toolkit"
    api_key = get_model_config_var(COHERE_API_KEY_ENV_VAR)

    def __init__(self, **kwargs: Any):
        # Override the environment variable from the request
        self.client = cohere.Client(api_key=self.api_key, client_name=self.client_name)

    @property
    def rerank_enabled(self) -> bool:
        return True

    @classmethod
    def list_models(cls) -> List[str]:
        if not CohereDeployment.is_available():
            return []

        url = "https://api.cohere.ai/v1/models"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {cls.api_key}",
        }

        response = requests.get(url, headers=headers)

        if not response.ok:
            logging.warning("Couldn't get models from Cohere API.")
            return []

        models = response.json()["models"]
        return [
            model["name"]
            for model in models
            if model.get("endpoints") and "chat" in model["endpoints"]
        ]

    @classmethod
    def is_available(cls) -> bool:
        return all([os.environ.get(var) is not None for var in COHERE_ENV_VARS])

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

    @collect_metrics_rerank
    def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        return self.client.rerank(
            query=query, documents=documents, model=DEFAULT_RERANK_MODEL, **kwargs
        )
