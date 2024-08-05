from typing import Any, AsyncGenerator, Dict, List

import cohere

from backend.chat.collate import to_dict
from backend.config.settings import Settings
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from backend.services.metrics import collect_metrics_chat_stream, collect_metrics_rerank

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

    azure_config = Settings().deployments.azure
    default_api_key = azure_config.api_key
    default_chat_endpoint_url = azure_config.endpoint_url

    def __init__(self, **kwargs: Any):
        # Override the environment variable from the request
        self.api_key = get_model_config_var(
            AZURE_API_KEY_ENV_VAR, AzureDeployment.default_api_key, **kwargs
        )
        self.chat_endpoint_url = get_model_config_var(
            AZURE_CHAT_URL_ENV_VAR, AzureDeployment.default_chat_endpoint_url, **kwargs
        )

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
        if not cls.is_available():
            return []

        return cls.DEFAULT_MODELS

    @classmethod
    def is_available(cls) -> bool:
        return (
            AzureDeployment.default_api_key is not None
            and AzureDeployment.default_chat_endpoint_url is not None
        )

    async def invoke_chat(self, chat_request: CohereChatRequest) -> Any:
        response = self.client.chat(
            **chat_request.model_dump(exclude={"stream", "file_ids", "agent_id"}),
        )
        yield to_dict(response)

    @collect_metrics_chat_stream
    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs
    ) -> AsyncGenerator[Any, Any]:
        stream = self.client.chat_stream(
            **chat_request.model_dump(exclude={"stream", "file_ids", "agent_id"}),
        )

        for event in stream:
            yield to_dict(event)

    @collect_metrics_rerank
    async def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], ctx: Context
    ) -> Any:
        return None
