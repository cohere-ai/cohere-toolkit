import asyncio
import json
import logging
import os
import threading
import time
from typing import Any, Dict, Generator, List

import cohere
import requests
from cohere.types import StreamedChatResponse

from backend.chat.collate import to_dict
from backend.chat.enums import StreamEvent
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest
from backend.services.metrics import report_metrics, run_in_new_thread

COHERE_API_KEY_ENV_VAR = "COHERE_API_KEY"
COHERE_ENV_VARS = [COHERE_API_KEY_ENV_VAR]


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

    def invoke_chat(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
        trace_id = kwargs.pop("trace_id", None)

        success = True
        response = {}
        try:
            response = self.client.chat(
                **chat_request.model_dump(exclude={"stream", "file_ids"}),
                **kwargs,
            )
        except Exception as e:
            success = False
            logging.error(f"Error invoking chat stream: {e}")

        self.report_metrics(
            endpoint_name="co.chat",
            success=success,
            trace_id=trace_id,
        )
        
        return to_dict(response)

    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        trace_id = kwargs.pop("trace_id", None)

        success = True
        try:
            stream = self.client.chat_stream(
                **chat_request.model_dump(exclude={"stream", "file_ids"}),
                **kwargs,
            )
        except Exception as e:
            success = False
            logging.error(f"Error invoking chat stream: {e}")

        for event in stream:
            event_dict = to_dict(event)
            
            if event_dict.get("finish_reason") == "ERROR":
                success = False
            
            yield event_dict


        self.report_metrics(
            endpoint_name="co.chat",
            success=success,
            trace_id=trace_id,
        )

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
        trace_id = kwargs.pop("trace_id", None)

        success = True
        try:
            response = self.client.rerank(
                query=query, documents=documents, model="rerank-english-v2.0", **kwargs
            )
        except Exception as e:
            self.report_metrics(
                endpoint_name="co.rerank",
                success=False,
                trace_id=trace_id,
            )
            raise e

        self.report_metrics(
            endpoint_name="co.rerank",
            success=success,
            trace_id=trace_id,
        )
        return response

    def invoke_tools(
        self,
        chat_request: CohereChatRequest,
        **kwargs: Any,
    ) -> Generator[StreamedChatResponse, None, None]:
        trace_id = kwargs.pop("trace_id", None)
        stream = self.client.chat_stream(
            message=message,
            tools=tools,
            model="command-r",
            force_single_step=True,
            chat_history=chat_history,
            **kwargs,
        )
        for event in stream:
            yield event.__dict__

        self.report_metrics(
            endpoint_name="co.chat",
            trace_id=trace_id,
        )

    def report_metrics(self, endpoint_name, success, trace_id) -> None:
        data = {
            "endpoint_name": endpoint_name,
            "method": "POST",
            "success": success,
            "trace_id": trace_id,
            "timestamp": time.time(),
        }
        threading.Thread(target=run_in_new_thread, args=(data,)).start()
