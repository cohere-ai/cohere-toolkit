from typing import Any, AsyncGenerator, Dict, List

import cohere

from backend.chat.collate import to_dict
from backend.config.settings import Settings
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from backend.services.metrics import collect_metrics_chat_stream, collect_metrics_rerank

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

    bedrock_config = Settings().deployments.bedrock
    region_name = bedrock_config.region_name
    access_key = bedrock_config.access_key
    secret_access_key = bedrock_config.secret_key
    session_token = bedrock_config.session_token

    def __init__(self, **kwargs: Any):
        self.client = cohere.BedrockClient(
            # TODO: remove hardcoded models once the SDK is updated
            chat_model="cohere.command-r-plus-v1:0",
            embed_model="cohere.embed-multilingual-v3",
            generate_model="cohere.command-text-v14",
            aws_access_key=get_model_config_var(
                BEDROCK_ACCESS_KEY_ENV_VAR, BedrockDeployment.access_key, **kwargs
            ),
            aws_secret_key=get_model_config_var(
                BEDROCK_SECRET_KEY_ENV_VAR,
                BedrockDeployment.secret_access_key,
                **kwargs,
            ),
            aws_session_token=get_model_config_var(
                BEDROCK_SESSION_TOKEN_ENV_VAR, BedrockDeployment.session_token, **kwargs
            ),
            aws_region=get_model_config_var(
                BEDROCK_REGION_NAME_ENV_VAR, BedrockDeployment.region_name, **kwargs
            ),
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
            BedrockDeployment.access_key is not None
            and BedrockDeployment.secret_access_key is not None
            and BedrockDeployment.session_token is not None
            and BedrockDeployment.region_name is not None
        )

    async def invoke_chat(self, chat_request: CohereChatRequest) -> Any:
        # bedrock accepts a subset of the chat request fields
        bedrock_chat_req = chat_request.model_dump(
            exclude={"tools", "conversation_id", "model", "stream"}, exclude_none=True
        )

        response = self.client.chat(
            **bedrock_chat_req,
        )
        yield to_dict(response)

    @collect_metrics_chat_stream
    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> AsyncGenerator[Any, Any]:
        # bedrock accepts a subset of the chat request fields
        bedrock_chat_req = chat_request.model_dump(
            exclude={"tools", "conversation_id", "model", "stream"}, exclude_none=True
        )

        stream = self.client.chat_stream(
            **bedrock_chat_req,
        )
        for event in stream:
            yield to_dict(event)

    @collect_metrics_rerank
    async def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], ctx: Context
    ) -> Any:
        return None
