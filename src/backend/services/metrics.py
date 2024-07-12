import asyncio
import json
import logging
import os
import time
import uuid
from functools import wraps
from typing import Any, Callable, Dict, Generator, Union

from cohere.core.api_error import ApiError
from httpx import AsyncHTTPTransport
from httpx._client import AsyncClient
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.chat.collate import to_dict
from backend.chat.enums import StreamEvent
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.metrics import (
    MetricsAgent,
    MetricsData,
    MetricsMessageType,
    MetricsSignal,
    MetricsUser,
)
from backend.services.auth.utils import get_header_user_id
import pdb

REPORT_ENDPOINT = os.getenv("REPORT_ENDPOINT", None)
REPORT_SECRET = os.getenv("REPORT_SECRET", None)
METRICS_LOGS_CURLS = os.getenv("METRICS_LOGS_CURLS", None)
NUM_RETRIES = 0
HEALTH_ENDPOINT = "health"
HEALTH_ENDPOINT_USER_ID = "health"

logger = logging.getLogger(__name__)


# TODO: update middleware to not have to do this mapping at all
# signals can simply specify event type
ROUTE_MAPPING: Dict[str, MetricsMessageType] = {
    # users
    "post /v1/users true": MetricsMessageType.USER_CREATED,
    "put /v1/users/:user_id true": MetricsMessageType.USER_UPDATED,
    "delete /v1/users/:user_id true": MetricsMessageType.USER_DELETED,
    # Chat
    "post /v1/chat-stream true": MetricsMessageType.CHAT_API_SUCCESS,
    "post /v1/chat-stream false": MetricsMessageType.CHAT_API_FAIL,
    "post co.chat true": MetricsMessageType.CHAT_API_SUCCESS,
    "post co.chat false": MetricsMessageType.CHAT_API_FAIL,
    # Rerank
    "post co.rerank true": MetricsMessageType.RERANK_API_SUCCESS,
    "post co.rerank false": MetricsMessageType.RERANK_API_FAIL,
    # agents
    "post /v1/agents true": MetricsMessageType.ASSISTANT_CREATED,
    "delete /v1/agents/:agent_id true": MetricsMessageType.ASSISTANT_DELETED,
    "put /v1/agents/:agent_id true": MetricsMessageType.ASSISTANT_UPDATED,
    "get /v1/agents/:agent_id true": MetricsMessageType.ASSISTANT_ACCESSED,
}


def event_name_of(
    method: str, endpoint_name: str, is_success: bool
) -> MetricsMessageType:
    key = f"{method} {endpoint_name} {is_success}"
    key = key.lower()
    if key in ROUTE_MAPPING:
        return ROUTE_MAPPING[key]
    return MetricsMessageType.UNKNOWN_SIGNAL


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        request.state.trace_id = str(uuid.uuid4())
        request.state.agent = None
        request.state.user = None
        request.state.model = None

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = time.perf_counter() - start_time

        data = self.get_event_data(request.scope, response, request, duration_ms)
        await run_loop(data)
        return response

    def get_event_data(self, scope, response, request, duration_ms) -> MetricsData:
        data = {}
        if scope["type"] != "http":
            return None
        method = self.get_method(scope)
        endpoint_name = self.get_endpoint_name(scope, request)
        is_success = self.get_success(response)
        message_type = event_name_of(method, endpoint_name, is_success)

        if message_type == MetricsMessageType.UNKNOWN_SIGNAL:
            logger.warning(
                f"cannot determine message type: {method} | {endpoint_name} | {is_success}"
            )
            return None

        try:
            user_id = get_header_user_id(request)
        except:
            logger.warning(f"Failed to get user id - {endpoint_name}")
            return None

        agent = self.get_agent(request)
        agent_id = agent.id if agent else None
        user = self.get_user(request)
        object_ids = self.get_object_ids(request)
        event_id = str(uuid.uuid4())

        return MetricsData(
            id=event_id,
            user_id=user_id,
            user=user,
            message_type=message_type,
            trace_id=request.state.trace_id,
            object_ids=object_ids,
            assistant=agent,
            model=request.state.model,
            assistant_id=agent_id,
            duration_ms=duration_ms,
        )

    def get_method(self, scope: dict) -> str:
        try:
            return scope["method"].lower()
        except KeyError:
            return "unknown"
        except Exception as e:
            logger.warning(f"Failed to get method:  {e}")
            return "unknown"

    def get_endpoint_name(self, scope: dict, request: Request) -> str:
        try:
            path = scope["path"]
            # Replace path parameters with their names
            for key, value in request.path_params.items():
                path = path.replace(value, f":{key}")

            path = path[:-1] if path.endswith("/") else path
            return path.lower()
        except KeyError:
            return "unknown"
        except Exception as e:
            logger.warning(f"Failed to get endpoint name: {e}")
            return "unknown"

    def get_success(self, response: Response) -> bool:
        try:
            return 200 <= response.status_code < 300
        except Exception as e:
            logger.warning(f"Failed to get success: {e}")
            return False

    def get_user_id(self, request: Request) -> Union[str, None]:
        try:
            user_id = request.headers.get("User-Id", None)

            if not user_id:
                user_id = (
                    request.state.user.id
                    if hasattr(request.state, "user") and request.state.user
                    else None
                )

            # Health check does not have a user id - use a placeholder
            if not user_id and HEALTH_ENDPOINT in request.url.path:
                return HEALTH_ENDPOINT_USER_ID

            return user_id
        except Exception as e:
            logger.warning(f"Failed to get user id: {e}")
            return None

    def get_user(self, request: Request) -> Union[MetricsUser, None]:
        if not hasattr(request.state, "user") or not request.state.user:
            return None

        try:
            return MetricsUser(
                id=request.state.user.id,
                fullname=request.state.user.fullname,
                email=request.state.user.email,
            )
        except Exception as e:
            logger.warning(f"Failed to get user: {e}")
            return None

    def get_object_ids(self, request: Request) -> Dict[str, str]:
        object_ids = {}
        try:
            for key, value in request.path_params.items():
                object_ids[key] = value

            for key, value in request.query_params.items():
                object_ids[key] = value

            return object_ids
        except Exception as e:
            logger.warning(f"Failed to get object ids: {e}")
            return {}

    def get_agent(self, request: Request) -> Union[MetricsAgent, None]:
        if not hasattr(request.state, "agent") or not request.state.agent:
            return None
        return request.state.agent


async def report_metrics(data: MetricsData | None) -> None:
    if not data:
        raise ValueError("No metrics data to report")

    data = attach_secret(data)
    signal = MetricsSignal(signal=data)
    if METRICS_LOGS_CURLS == "true":
        log_signal_curl(signal)

    if not REPORT_SECRET:
        logger.error("No report secret set")
        return

    if not REPORT_ENDPOINT:
        logger.error("No report endpoint set")
        return

    if not isinstance(signal, dict):
        signal = to_dict(signal)
    transport = AsyncHTTPTransport(retries=NUM_RETRIES)
    try:
        async with AsyncClient(transport=transport) as client:
            await client.post(REPORT_ENDPOINT, json=signal)
    except Exception as e:
        logger.error(f"Failed to report metrics: {e}")


def attach_secret(data: MetricsData) -> MetricsData:
    if not REPORT_SECRET:
        return data
    data.secret = REPORT_SECRET
    return data


# TODO: remove the logging once metrics are configured correctly
def log_signal_curl(signal: MetricsSignal) -> None:
    s = to_dict(signal)
    s["signal"]["secret"] = "'$SECRET'"
    json_signal = json.dumps(s)
    # just general curl commands to test the endpoint for now
    logger.info(
        f"\n\ncurl -X POST -H \"Content-Type: application/json\" -d '{json_signal}' $ENDPOINT\n\n"
    )


async def run_loop(metrics_data: MetricsData) -> None:
    async def report_metrics_with_error_handling():
        try:
            await report_metrics(metrics_data)
        except Exception as e:
            logger.error(f"Failed to execute report_metrics task: {e}")

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    task = loop.create_task(report_metrics_with_error_handling())


# DECORATORS
def collect_metrics_chat(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        metrics_data = initialize_sdk_metrics_data("chat", chat_request, **kwargs)

        response_dict = {}
        try:
            response = func(self, chat_request, **kwargs)
            response_dict = to_dict(response)
        except Exception as e:
            metrics_data = handle_error(metrics_data, e)
            raise e
        finally:
            (
                metrics_data.input_tokens,
                metrics_data.output_tokens,
            ) = get_input_output_tokens(response_dict)
            metrics_data.duration_ms = time.perf_counter() - start_time
            await run_loop(metrics_data)

            return response_dict

    return wrapper

import pdb
def collect_metrics_chat_stream(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        metrics_data, kwargs = initialize_sdk_metrics_data(
            "chat", chat_request, **kwargs
        )
        stream = func(self, chat_request, **kwargs)

        try:
            async for event in stream:
                pdb.set_trace()
                event_dict = to_dict(event)

                if is_event_end_with_error(event_dict):
                    metrics_data.success = False
                    metrics_data.error = event_dict.get("error")

                if event_dict.get("event_type") == StreamEvent.STREAM_END:
                    (
                        metrics_data.input_nb_tokens,
                        metrics_data.output_nb_tokens,
                    ) = get_input_output_tokens(event_dict.get("response"))

                yield event_dict
        except Exception as e:
            metrics_data = handle_error(metrics_data, e)
            raise e
        finally:
            metrics_data.duration_ms = time.perf_counter() - start_time
            await run_loop(metrics_data)

    return wrapper


def collect_metrics_rerank(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(
        self, query: str, documents: Dict[str, Any], **kwargs: Any
    ) -> Any:
        start_time = time.perf_counter()
        metrics_data, kwargs = initialize_sdk_metrics_data("rerank", None, **kwargs)

        response_dict = {}
        try:
            response = await func(self, query, documents, **kwargs)
            response_dict = to_dict(response)
            metrics_data.search_units = get_search_units(response_dict)
        except Exception as e:
            metrics_data = handle_error(metrics_data, e)
            raise e
        finally:
            metrics_data.duration_ms = time.perf_counter() - start_time
            await run_loop(metrics_data)
            return response_dict

    return wrapper


def initialize_sdk_metrics_data(
    func_name: str, chat_request: CohereChatRequest, **kwargs: Any
) -> tuple[MetricsData, Any]:

    model = kwargs.get("model", None)
    trace_id = kwargs.get("trace_id", None)
    user_id = kwargs.get("user_id", None)
    assistant_id = kwargs.get("agent_id", None)
    method = "POST"
    endpoint_name = f"co.{func_name}"
    is_success = True
    message_type = event_name_of(method, endpoint_name, is_success)

    return (
        MetricsData(
            id=str(uuid.uuid4()),
            message_type=message_type,
            trace_id=trace_id,
            user_id=user_id,
            assistant_id=assistant_id,
            model=model,
        ),
        kwargs,
    )


def get_input_output_tokens(response_dict: dict) -> tuple[int, int]:
    if response_dict is None:
        return None, None

    input_tokens = (
        response_dict.get("meta", {}).get("billed_units", {}).get("input_tokens")
    )
    output_tokens = (
        response_dict.get("meta", {}).get("billed_units", {}).get("output_tokens")
    )
    return input_tokens, output_tokens


def get_search_units(response_dict: dict) -> int:
    return response_dict.get("meta", {}).get("billed_units", {}).get("search_units")


def is_event_end_with_error(event_dict: dict) -> bool:
    return (
        event_dict.get("event_type") == StreamEvent.STREAM_END
        and event_dict.get("finish_reason") != "COMPLETE"
        and event_dict.get("finish_reason") != "MAX_TOKENS"
    )


def handle_error(metrics_data: MetricsData, e: Exception) -> None:
    metrics_data.success = False
    metrics_data.error = str(e)
    if isinstance(e, ApiError):
        metrics_data.status_code = e.status_code
    return metrics_data
