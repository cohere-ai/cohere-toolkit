import logging
import os
from typing import Any, Dict, Generator, List

import cohere
import requests
from cohere.types import StreamedChatResponse

from backend.chat.custom.model_deployments.base import BaseDeployment
from backend.schemas.cohere_chat import CohereChatRequest


class CohereDeployment(BaseDeployment):
    """Cohere Platform Deployment."""

    api_key = os.environ.get("COHERE_API_KEY")
    client_name = "cohere-toolkit"

    def __init__(self):
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
        return [model["name"] for model in models if "chat" in model["endpoints"]]

    @classmethod
    def is_available(cls) -> bool:
        return cls.api_key is not None

    def invoke_chat(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
        return self.client.chat(
            **chat_request.model_dump(exclude={"stream"}),
            **kwargs,
        )

    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        stream = self.client.chat_stream(
            **chat_request.model_dump(exclude={"stream"}),
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
        return self.client.rerank(
            query=query, documents=documents, model="rerank-english-v2.0", **kwargs
        )

    def invoke_tools(self, message: str, tools: List[Any], **kwargs: Any) -> List[Any]:
        return self.client.chat(
            message=message, tools=tools, model="command-r", **kwargs
        )
