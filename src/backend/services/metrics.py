import asyncio
import json
import logging
import os
import time
import uuid
from functools import wraps
from typing import Any, Callable, Dict, Generator, Union

from cohere.core.api_error import ApiError
from fastapi import BackgroundTasks
from httpx import AsyncHTTPTransport
from httpx._client import AsyncClient
from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.chat.collate import to_dict
from backend.chat.enums import StreamEvent
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.metrics import (
    MetricsAgent,
    MetricsChat,
    MetricsData,
    MetricsMessageType,
    MetricsSignal,
    MetricsUser,
)
from backend.services.auth.utils import get_header_user_id
from backend.services.generators import AsyncGeneratorContextManager

REPORT_ENDPOINT = os.getenv("REPORT_ENDPOINT", None)
REPORT_SECRET = os.getenv("REPORT_SECRET", None)
METRICS_LOGS_CURLS = os.getenv("METRICS_LOGS_CURLS", None)
NUM_RETRIES = 0
HEALTH_ENDPOINT = "health"
HEALTH_ENDPOINT_USER_ID = "health"

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):

        self._confirm_env()
        self._init_req_state(request)

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = time.perf_counter() - start_time
        self._send_signal(request, response, duration_ms)

        return response

    def _init_req_state(self, request: Request) -> None:
        request.state.trace_id = str(uuid.uuid4())
        request.state.agent = None
        request.state.model = None
        request.state.rerank_model = None
        request.state.stream_start = None
        request.state.user = None
        request.state.event_type = None

    def _confirm_env(self):
        if not REPORT_SECRET:
            logger.warning("No report secret set")
        if not REPORT_ENDPOINT:
            logger.warning("No report endpoint set")

    def _send_signal(
        self, request: Request, response: Response, duration_ms: float
    ) -> None:
        signal = self._get_event_signal(request, response, duration_ms)
        should_send_event = request.state.event_type and signal
        if should_send_event:
            response.background = BackgroundTask(report_metrics, signal)

    def _get_event_signal(
        self, request: Request, response: Response, duration_ms: float
    ) -> MetricsSignal | None:

        if request.scope["type"] != "http":
            return None

        message_type = request.state.event_type
        if not message_type:
            return None

        user = self._get_user(request)
        # when user is created, user_id is not in the header
        user_id = (
            user.id
            if message_type == MetricsMessageType.USER_CREATED
            else get_header_user_id(request)
        )
        agent = get_agent(request)
        agent_id = agent.id if agent else None
        event_id = str(uuid.uuid4())
        now_unix_seconds = time.time()

        try:
            data = MetricsData(
                id=event_id,
                user_id=user_id,
                timestamp=now_unix_seconds,
                user=user,
                message_type=message_type,
                trace_id=request.state.trace_id,
                assistant=agent,
                assistant_id=agent_id,
                duration_ms=duration_ms,
            )
            data = self._attach_secret(data)
            signal = MetricsSignal(signal=data)
            return signal
        except Exception as e:
            logger.warning(f"Failed to process event data: {e}")
            return None

    def _get_user(self, request: Request) -> Union[MetricsUser, None]:
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

    def _attach_secret(self, data: MetricsData) -> MetricsData:
        if not REPORT_SECRET:
            return data
        data.secret = REPORT_SECRET
        return data


async def report_metrics(signal: MetricsSignal) -> None:
    if METRICS_LOGS_CURLS == "true":
        log_signal_curl(signal)
    if not REPORT_SECRET:
        return
    if not REPORT_ENDPOINT:
        return

    try:
        signal = to_dict(signal)
        transport = AsyncHTTPTransport(retries=NUM_RETRIES)
        async with AsyncClient(transport=transport) as client:
            await client.post(REPORT_ENDPOINT, json=signal)
    except Exception as e:
        logger.error(f"Failed to report metrics: {e}")


def collect_metrics_chat_stream(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs: Any) -> Any:
        stream = func(*args, **kwargs)
        async for v in stream:
            report_streaming_chat_event(v, **kwargs)
            yield v

    return wrapper


def collect_metrics_rerank(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(
        self, query: str, documents: Dict[str, Any], **kwargs: Any
    ) -> Any:
        start_time = time.perf_counter()
        try:
            response = await func(self, query, documents, **kwargs)
            duration_ms = time.perf_counter() - start_time
            report_rerank_metrics(response, duration_ms, **kwargs)
            return response
        except Exception as e:
            duration_ms = time.perf_counter() - start_time
            metrics_data = report_rerank_failed_metrics(duration_ms, e, **kwargs)
            raise e

    return wrapper


# TODO: remove the logging once metrics are configured correctly
def log_signal_curl(signal: MetricsSignal) -> None:
    s = to_dict(signal)
    s["signal"]["secret"] = "'$SECRET'"
    json_signal = json.dumps(s)
    # just general curl commands to test the endpoint for now
    logger.info(
        f"\n\ncurl -X POST -H \"Content-Type: application/json\" -d '{json_signal}' $ENDPOINT\n\n"
    )


# DO NOT THROW EXPCEPTIONS IN THIS FUNCTION
def report_streaming_chat_event(event: dict[str, Any], **kwargs: Any) -> None:
    try:
        request = kwargs.get("request", None)
        if not request:
            raise ValueError("request not set")
        event_type = event["event_type"]
        if event_type == StreamEvent.STREAM_START:
            request.state.stream_start = time.perf_counter()

        if event_type != StreamEvent.STREAM_END:
            return

        start_time = request.state.stream_start
        duration_ms = (
            None if not start_time else time.perf_counter() - request.state.stream_start
        )
        trace_id = request.state.trace_id
        model = request.state.model
        user_id = get_header_user_id(request)
        agent = get_agent(request)
        agent_id = agent.id if agent else None
        event_dict = to_dict(event).get("response", {})
        input_tokens = (
            event_dict.get("meta", {}).get("billed_units", {}).get("input_tokens", 0)
        )
        output_tokens = (
            event_dict.get("meta", {}).get("billed_units", {}).get("output_tokens", 0)
        )
        search_units = (
            event_dict.get("meta", {}).get("billed_units", {}).get("search_units", 0)
        )
        search_units = search_units if search_units else 0
        is_error = (
            event_dict.get("event_type") == StreamEvent.STREAM_END
            and event_dict.get("finish_reason") != "COMPLETE"
            and event_dict.get("finish_reason") != "MAX_TOKENS"
        )

        message_type = (
            MetricsMessageType.CHAT_API_FAIL
            if is_error
            else MetricsMessageType.CHAT_API_SUCCESS
        )
        # validate successful event metrics
        if not is_error:
            chat_metrics = MetricsChat(
                input_nb_tokens=input_tokens,
                output_nb_tokens=output_tokens,
                search_units=search_units,
                model=model,
                assistant_id=agent_id,
            )

        metrics = MetricsData(
            id=str(uuid.uuid4()),
            user_id=user_id,
            trace_id=trace_id,
            duration_ms=duration_ms,
            message_type=message_type,
            timestamp=time.time(),
            input_nb_tokens=input_tokens,
            output_nb_tokens=output_tokens,
            search_units=search_units,
            model=model,
            assistant_id=agent_id,
            assistant=agent,
            error=event_dict.get("finish_reason", None) if is_error else None,
        )
        signal = MetricsSignal(signal=metrics)
        # do not await, fire and forget
        asyncio.create_task(report_metrics(signal))

    except Exception as e:
        logger.error(f"Failed to report streaming event: {e}")


def get_agent(request: Request) -> Union[MetricsAgent, None]:
    if not hasattr(request.state, "agent") or not request.state.agent:
        return None
    return request.state.agent


# DO NOT THROW EXPCEPTIONS IN THIS FUNCTION
def report_rerank_metrics(response: Any, duration_ms: float, **kwargs: Any):
    try:
        request = kwargs.get("request", None)
        if not request:
            raise ValueError("request not set")
        trace_id = request.state.trace_id
        model = request.state.rerank_model
        user_id = get_header_user_id(request)
        agent = get_agent(request)
        agent_id = agent.id if agent else None
        response_dict = to_dict(response)
        search_units = (
            response_dict.get("meta", {}).get("billed_units", {}).get("search_units")
        )
        message_type = MetricsMessageType.RERANK_API_SUCCESS

        # ensure valid MetricsChat object
        chat_metrics = MetricsChat(
            input_nb_tokens=0,
            output_nb_tokens=0,
            search_units=search_units,
            model=model,
            assistant_id=agent_id,
        )

        metrics_data = MetricsData(
            id=str(uuid.uuid4()),
            message_type=message_type,
            trace_id=trace_id,
            user_id=user_id,
            assistant_id=agent_id,
            assistant=agent,
            model=model,
            search_units=search_units,
            timestamp=time.time(),
            duration_ms=duration_ms,
        )

        signal = MetricsSignal(signal=metrics_data)
        asyncio.create_task(report_metrics(signal))
    except Exception as e:
        logger.error(f"Failed to report rerank metrics: {e}")


def report_rerank_failed_metrics(duration_ms: float, error: Exception, **kwargs: Any):
    try:
        request = kwargs.get("request", None)
        if not request:
            raise ValueError("request not set")
        trace_id = request.state.trace_id
        model = request.state.rerank_model
        user_id = get_header_user_id(request)
        agent = get_agent(request)
        agent_id = agent.id if agent else None
        message_type = MetricsMessageType.RERANK_API_FAIL
        error_message = str(error)
        metrics_data = MetricsData(
            id=str(uuid.uuid4()),
            message_type=message_type,
            trace_id=trace_id,
            user_id=user_id,
            assistant_id=agent_id,
            assistant=agent,
            model=model,
            search_units=search_units,
            duration_ms=duration_ms,
            timestamp=time.time(),
            error=error_message,
        )
        signal = MetricsSignal(signal=metrics_data)
        asyncio.create_task(report_metrics(signal))
    except Exception as e:
        logger.error(f"Failed to report rerank metrics: {e}")
