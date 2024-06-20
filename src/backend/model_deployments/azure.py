import logging
import os
import threading
import time
from typing import Any, Dict, Generator, List

import cohere
from cohere.core.api_error import ApiError
from cohere.types import StreamedChatResponse

from backend.chat.collate import to_dict
from backend.chat.enums import StreamEvent
from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.metrics import MetricsData
from backend.services.metrics import hash_string, report_metrics_thread

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
        start_time = time.perf_counter()
        metrics_data = MetricsData(
            endpoint_name="co.chat",
            method="POST",
            trace_id=kwargs.pop("trace_id", None),
            user_id=kwargs.pop("user_id", None),
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
        except ApiError as e:
            metrics_data.success = False
            metrics_data.error = str(e)
            metrics_data.status_code = e.status_code
            raise e
        except Exception as e:
            metrics_data.success = False
            metrics_data.error = str(e)
            raise e
        finally:
            metrics_data.input_tokens = (
                response_dict.get("meta", {})
                .get("billed_units", {})
                .get("input_tokens")
            )
            metrics_data.output_tokens = (
                response_dict.get("meta", {})
                .get("billed_units", {})
                .get("output_tokens")
            )
            metrics_data.duration_ms = time.perf_counter() - start_time
            self.report_metrics(metrics_data)

            return response_dict

    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        start_time = time.perf_counter()
        metrics_data = MetricsData(
            endpoint_name="co.chat",
            method="POST",
            trace_id=kwargs.pop("trace_id", None),
            user_id=kwargs.pop("user_id", None),
            model=chat_request.model,
            success=True,
        )

        stream = self.client.chat_stream(
            **chat_request.model_dump(exclude={"stream", "file_ids"}),
            **kwargs,
        )

        try:
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
        except ApiError as e:
            metrics_data.success = False
            metrics_data.error = str(e)
            metrics_data.status_code = e.status_code
        except Exception as e:
            metrics_data.success = False
            metrics_data.error = str(e)
            raise e
        finally:
            metrics_data.duration_ms = time.perf_counter() - start_time
            self.report_metrics(metrics_data)

    def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        return None

    def report_metrics(self, metrics_data: MetricsData) -> None:
        threading.Thread(target=report_metrics_thread, args=(metrics_data,)).start()
