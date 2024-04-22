import os
from typing import Any, Dict, Generator, List

import cohere
from cohere.types import StreamedChatResponse

from backend.chat.custom.model_deployments.base import BaseDeployment
from backend.schemas.cohere_chat import CohereChatRequest


class AzureDeployment(BaseDeployment):
    """
    Azure Deployment.
    How to deploy a model:
    https://learn.microsoft.com/azure/ai-studio/how-to/deploy-models-cohere-command
    """

    api_key = os.environ.get("AZURE_API_KEY")
    # Example URL: "https://<endpoint>.<region>.inference.ai.azure.com/v1"
    # Note: It must have /v1 and it should not have /chat
    chat_endpoint_url = os.environ.get("AZURE_CHAT_ENDPOINT_URL")

    def __init__(self):
        if not self.chat_endpoint_url.endswith("/v1"):
            self.chat_endpoint_url = self.chat_endpoint_url + "/v1"
        self.client = cohere.Client(
            base_url=self.chat_endpoint_url, api_key=self.api_key
        )

    @property
    def rerank_enabled(self) -> bool:
        return False

    @classmethod
    def list_models(cls) -> List[str]:
        if not AzureDeployment.is_available():
            return []

        return ["azure-command"]

    @classmethod
    def is_available(cls) -> bool:
        return cls.api_key is not None and cls.chat_endpoint_url is not None

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
        return None

    def invoke_tools(self, message: str, tools: List[Any], **kwargs: Any) -> List[Any]:
        return self.client.chat(message=message, tools=tools, **kwargs)
