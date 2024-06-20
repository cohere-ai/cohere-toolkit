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

    def __init__(self, **kwargs: Any):
        self.client = cohere.BedrockClient(
            # TODO: remove hardcoded models once the SDK is updated
            chat_model="cohere.command-r-plus-v1:0",
            embed_model="cohere.embed-multilingual-v3",
            generate_model="cohere.command-text-v14",
            aws_access_key=get_model_config_var(BEDROCK_ACCESS_KEY_ENV_VAR, **kwargs),
            aws_secret_key=get_model_config_var(BEDROCK_SECRET_KEY_ENV_VAR, **kwargs),
            aws_session_token=get_model_config_var(
                BEDROCK_SESSION_TOKEN_ENV_VAR, **kwargs
            ),
            aws_region=get_model_config_var(BEDROCK_REGION_NAME_ENV_VAR, **kwargs),
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
        return all([os.environ.get(var) is not None for var in BEDROCK_ENV_VARS])

    def invoke_chat(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        metrics_data = MetricsData(
            endpoint_name="co.chat",
            method="POST",
            trace_id=kwargs.pop("trace_id", None),
            user_id_hash=hash_string(kwargs.pop("user_id", None)),
            model=chat_request.model,
            success=True,
        )

        response = {}
        # bedrock accepts a subset of the chat request fields
        bedrock_chat_req = chat_request.model_dump(
            exclude={"tools", "conversation_id", "model", "stream"}, exclude_none=True
        )

        try:
            yield self.client.chat(
                **bedrock_chat_req,
                **kwargs,
            )
            response_dict = to_dict(response)
        except ApiError as e:
            metrics_data.success = False
            metrics_data.error = str(e)
            metrics_data.status_code = e.status_code
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
            metrics_data.duration = time.perf_counter() - start_time

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
            user_id_hash=hash_string(kwargs.pop("user_id", None)),
            model=chat_request.model,
            success=True,
        )

        # bedrock accepts a subset of the chat request fields
        bedrock_chat_req = chat_request.model_dump(
            exclude={"tools", "conversation_id", "model", "stream"}, exclude_none=True
        )

        stream = self.client.chat_stream(
            **bedrock_chat_req,
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
            logging.error(f"Error invoking chat stream: {e}")
        finally:
            metrics_data.duration = time.perf_counter() - start_time
            self.report_metrics(metrics_data)

    def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        return None

    def report_metrics(self, metrics_data: MetricsData) -> None:
        threading.Thread(target=report_metrics_thread, args=(metrics_data,)).start()
