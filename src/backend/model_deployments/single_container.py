from typing import Any, AsyncGenerator

import cohere

from backend.chat.collate import to_dict
from backend.config.settings import Settings
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context

DEFAULT_RERANK_MODEL = "rerank-english-v2.0"
SC_URL_ENV_VAR = "SINGLE_CONTAINER_URL"
SC_MODEL_ENV_VAR = "SINGLE_CONTAINER_MODEL"


class SingleContainerDeployment(BaseDeployment):
    """Single Container Deployment."""

    client_name = "cohere-toolkit"
    sc_config = Settings().get('deployments.single_container')
    default_url = sc_config.url
    default_model = sc_config.model

    def __init__(self, **kwargs: Any):
        self.url = get_model_config_var(
            SC_URL_ENV_VAR, SingleContainerDeployment.default_url, **kwargs
        )
        self.model = get_model_config_var(
            SC_MODEL_ENV_VAR, SingleContainerDeployment.default_model, **kwargs
        )
        self.client = cohere.Client(
            base_url=self.url, client_name=self.client_name, api_key="none"
        )

    @staticmethod
    def name() -> str:
        return "Single Container"

    @staticmethod
    def env_vars() -> list[str]:
        return [SC_URL_ENV_VAR, SC_MODEL_ENV_VAR]

    @staticmethod
    def rerank_enabled() -> bool:
        return SingleContainerDeployment.default_model.startswith("rerank")

    @classmethod
    def list_models(cls) -> list[str]:
        if not SingleContainerDeployment.is_available():
            return []

        return [SingleContainerDeployment.default_model]

    @staticmethod
    def is_available() -> bool:
        return (
            SingleContainerDeployment.default_model is not None
            and SingleContainerDeployment.default_url is not None
        )

    async def invoke_chat(self, chat_request: CohereChatRequest, **kwargs) -> Any:
        response = self.client.chat(
            **chat_request.model_dump(
                exclude={"stream", "file_ids", "model", "agent_id"}
            ),
        )
        yield to_dict(response)

    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> AsyncGenerator[Any, Any]:
        stream = self.client.chat_stream(
            **chat_request.model_dump(
                exclude={"stream", "file_ids", "model", "agent_id"}
            ),
        )

        for event in stream:
            yield to_dict(event)

    async def invoke_rerank(
        self, query: str, documents: list[str], ctx: Context, **kwargs
    ) -> Any:
        return self.client.rerank(
            query=query, documents=documents, model=DEFAULT_RERANK_MODEL
        )
