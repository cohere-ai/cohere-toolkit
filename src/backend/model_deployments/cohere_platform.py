import logging
import os
import threading
from typing import Any, Dict, Generator, List

import cohere
import requests
from cohere.types import StreamedChatResponse

from backend.chat.collate import to_dict
from backend.chat.enums import StreamEvent
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.metrics import MetricsData
from backend.services.metrics import hash_string, report_metrics_thread

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
        metrics_data = MetricsData(
            endpoint_name="co.chat",
            method="POST",
            trace_id=kwargs.pop("trace_id", None),
            user_id_hash=hash_string(kwargs.pop("user_id", None)),
            model=chat_request.model,
            success=True,
        )

        response = {}
        try:
            response = self.client.chat(
                **chat_request.model_dump(exclude={"stream", "file_ids"}),
                **kwargs,
            )
            response_dict = to_dict(response)
        except Exception as e:
            metrics_data.success = False
            metrics_data.error = str(e)
            logging.error(f"Error invoking chat stream: {e}")

        metrics_data.input_tokens = (
            response_dict.get("meta", {}).get("billed_units", {}).get("input_tokens")
        )
        metrics_data.output_tokens = (
            response_dict.get("meta", {}).get("billed_units", {}).get("output_tokens")
        )

        self.report_metrics(metrics_data)

        return response_dict

    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        metrics_data = MetricsData(
            endpoint_name="co.chat",
            method="POST",
            trace_id=kwargs.pop("trace_id", None),
            user_id_hash=hash_string(kwargs.pop("user_id", None)),
            model=chat_request.model,
            success=True,
        )

        stream = []
        try:
            stream = self.client.chat_stream(
                **chat_request.model_dump(exclude={"stream", "file_ids"}),
                **kwargs,
            )
        except Exception as e:
            metrics_data.success = False
            metrics_data.error = str(e)
            logging.error(f"Error invoking chat stream: {e}")

        for event in stream:
            event_dict = to_dict(event)

            if (
                event_dict.get("event_type") == StreamEvent.STREAM_END
                and event_dict.get("finish_reason") != "COMPLETE"
                and event_dict.get("event") != "MAX_TOKENS"
            ):
                metrics_data.success = False
                metrics_data.error = event_dict.get("error")

            if event_dict.get("event_type") == StreamEvent.STREAM_END:
                metrics_data.input_nb_tokens = (
                    event_dict.get("response", {})
                    .get("meta", {})
                    .get("billed_units", {})
                    .get("input_tokens")
                )
                metrics_data.output_nb_tokens = (
                    event_dict.get("response", {})
                    .get("meta", {})
                    .get("billed_units", {})
                    .get("output_tokens")
                )

            yield event_dict

        self.report_metrics(metrics_data)

    def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        model = "rerank-english-v2.0"
        metrics_data = MetricsData(
            endpoint_name="co.rerank",
            method="POST",
            trace_id=kwargs.pop("trace_id", None),
            user_id_hash=hash_string(kwargs.pop("user_id", None)),
            model=model,
            success=True,
        )

        response = {}
        try:
            response = self.client.rerank(
                query=query, documents=documents, model=model, **kwargs
            )
            response_dict = to_dict(response)
        except Exception as e:
            metrics_data.success = False
            metrics_data.error = str(e)
            logging.error(f"Error invoking rerank: {e}")

        metrics_data.search_units = (
            response_dict.get("meta", {}).get("billed_units", {}).get("search_units")
        )

        self.report_metrics(metrics_data)
        return response_dict

    def report_metrics(self, metrics_data: MetricsData) -> None:
        threading.Thread(target=report_metrics_thread, args=(metrics_data,)).start()
