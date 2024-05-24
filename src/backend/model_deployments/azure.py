import os
from typing import Any, Dict, Generator, List

import cohere
from cohere.types import StreamedChatResponse

from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest

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
