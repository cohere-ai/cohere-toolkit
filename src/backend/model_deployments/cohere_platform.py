from typing import Any, Dict, List

import cohere
import requests
import json
import aiohttp

from backend.chat.collate import to_dict
from backend.config.settings import Settings
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from backend.services.logger.utils import LoggerFactory

COHERE_API_KEY_ENV_VAR = "COHERE_API_KEY"
COHERE_ENV_VARS = [COHERE_API_KEY_ENV_VAR]
DEFAULT_RERANK_MODEL = "rerank-english-v2.0"


class CohereDeployment(BaseDeployment):
    """Cohere Platform Deployment."""

    client_name = "cohere-toolkit"
    api_key = Settings().get('deployments.cohere_platform.api_key')

    def __init__(self, **kwargs: Any):
        # Override the environment variable from the request
        api_key = get_model_config_var(
            COHERE_API_KEY_ENV_VAR, CohereDeployment.api_key, **kwargs
        )
        self.client = cohere.Client(api_key, client_name=self.client_name)

    @property
    def rerank_enabled(self) -> bool:
        return True

    @classmethod
    def list_models(cls) -> List[str]:
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

    @classmethod
    def is_available(cls) -> bool:
        return CohereDeployment.api_key is not None

    async def invoke_chat(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> Any:
        response = self.client.chat(
            **chat_request.model_dump(exclude={"stream", "file_ids", "agent_id"}),
        )
        yield to_dict(response)

    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> Any:
        print(chat_request.model_dump())
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                "https://cohere.usw-16.palantirfoundry.com/contour-backend-multiplexer/api/module-group-multiplexer/compute-modules/jobs/execute",
                headers={
                    "accept": "*/*",
                    "authorization": "Bearer xxx",
                    "content-type": "application/json",
                },
                json={
                    "deployedAppRid": "ri.foundry.main.deployed-app.811b08c3-0247-4e06-aa14-b2970671e38d",
                    "deployedAppBranch": "master",
                    "queryType": "chatStream",
                    "query": chat_request.model_dump(exclude_none=True, include={"message", "chat_history", "documents"}),
                },
            ) as r:
                async for line in r.content:
                    print(json.loads(line))
                    yield json.loads(line)


    async def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], ctx: Context, **kwargs: Any
    ) -> Any:
        response = self.client.rerank(
            query=query, documents=documents, model=DEFAULT_RERANK_MODEL
        )
        return to_dict(response)
