from typing import Any

import cohere
import requests

from backend.chat.collate import to_dict
from backend.config.settings import Settings
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from backend.services.logger.utils import LoggerFactory

COHERE_API_KEY_ENV_VAR = "COHERE_API_KEY"
DEFAULT_RERANK_MODEL = "rerank-english-v2.0"


class CohereDeployment(BaseDeployment):
    """Cohere Platform Deployment."""

    client_name = "cohere-toolkit"
    api_key = Settings().get('deployments.cohere_platform.api_key')

    def __init__(self, **kwargs: Any):
        # Override the environment variable from the request
        super().__init__(**kwargs)
        api_key = get_model_config_var(
            COHERE_API_KEY_ENV_VAR, CohereDeployment.api_key, **kwargs
        )
        self.client = cohere.Client(api_key, client_name=self.client_name)

    @staticmethod
    def name() -> str:
        return "Cohere Platform"

    @staticmethod
    def env_vars() -> list[str]:
        return [COHERE_API_KEY_ENV_VAR]

    @staticmethod
    def rerank_enabled() -> bool:
        return True

    @classmethod
    def list_models(cls) -> list[str]:
        logger = LoggerFactory().get_logger()
        if not CohereDeployment.is_available():
            return []

        url = "https://api.cohere.ai/v1/models"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {cls.api_key}",
        }

        response = requests.get(url, headers=headers)

        if not response.ok:
            logger.warning(
                event=f"[Cohere Deployment] Error retrieving models: Invalid HTTP {response.status_code} response",
            )
            return []

        models = response.json()["models"]
        return [model["name"] for model in models if model.get("endpoints") and "chat" in model["endpoints"]]

    @staticmethod
    def is_available() -> bool:
        return CohereDeployment.api_key is not None

    async def invoke_chat(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Any:
        response = self.client.chat(
            **chat_request.model_dump(exclude={"stream", "file_ids", "agent_id"}),
        )
        yield to_dict(response)

    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> Any:
        logger = ctx.get_logger()

        stream = self.client.chat_stream(
            **chat_request.model_dump(exclude={"stream", "file_ids", "agent_id"}),
        )

        for event in stream:
            event_dict = to_dict(event)

            event_dict_log = event_dict.copy()
            event_dict_log.pop("conversation_id", None)
            logger.debug(
                event="Chat event",
                **event_dict_log,
                conversation_id=ctx.get_conversation_id(),
            )

            yield event_dict

    async def invoke_rerank(
        self, query: str, documents: list[str], ctx: Context, **kwargs: Any
    ) -> Any:
        response = self.client.rerank(
            query=query, documents=documents, model=DEFAULT_RERANK_MODEL
        )
        return to_dict(response)
