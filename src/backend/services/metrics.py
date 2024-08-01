import asyncio
import json
import os
import time
import uuid
from functools import wraps
from typing import Any, Callable, Dict, Optional

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
from backend.schemas.context import Context
from backend.schemas.metrics import (
    MetricsData,
    MetricsMessageType,
    MetricsModelAttrs,
    MetricsSignal,
)
from backend.services.context import get_context
from backend.services.logger.utils import LoggerFactory

REPORT_ENDPOINT = os.getenv("REPORT_ENDPOINT", None)
REPORT_SECRET = os.getenv("REPORT_SECRET", None)
METRICS_LOGS_CURLS = os.getenv("METRICS_LOGS_CURLS", None)
NUM_RETRIES = 0
HEALTH_ENDPOINT = "health"
HEALTH_ENDPOINT_USER_ID = "health"
# TODO: fix this hack eventually
DEFAULT_RERANK_MODEL = "rerank-english-v2.0"


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware class for handling metrics in the application.

    This middleware is responsible for tracking and reporting select events for incoming requests.
    It follows the fire and forget mechanism and should never throw exceptions.
    For chat streams, and rerank events, additional decorators are also required.

    Attributes:
        None

    Methods:
        dispatch: Dispatches the request to the next middleware or application handler.
        _init_req_state: Initializes the state of the request.
        _confirm_env: Confirms the environment setup for reporting metrics.
        _send_signal: Sends the metrics signal to the reporting endpoint.
        _get_event_signal: Retrieves the metrics signal for the current request.
        _get_user: Retrieves the user information from the request.
        _attach_secret: Attaches the report secret to the metrics data.

    """

    async def dispatch(self, request: Request, call_next: Callable):
        self._confirm_env()

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = time.perf_counter() - start_time

        ctx = get_context(request)
        self._send_signal(request, response, duration_ms, ctx)

        return response

    def _confirm_env(self):
        logger = LoggerFactory().get_logger()
        if not REPORT_SECRET:
            logger.warning(event="[Metrics] No report secret set")
        if not REPORT_ENDPOINT:
            logger.warning(event="[Metrics] No report endpoint set")

    def _should_send_signal(
        self,
        signal: Optional[MetricsSignal],
        event_type: Optional[MetricsMessageType],
        response: Response,
    ) -> bool:
        middleware_allowed_signals = {
            MetricsMessageType.USER_CREATED,
            MetricsMessageType.USER_UPDATED,
            MetricsMessageType.USER_DELETED,
            MetricsMessageType.ASSISTANT_CREATED,
            MetricsMessageType.ASSISTANT_UPDATED,
            MetricsMessageType.ASSISTANT_DELETED,
            MetricsMessageType.ASSISTANT_ACCESSED,
        }

        return (
            True
            if (
                event_type in middleware_allowed_signals
                and signal
                # TODO: we may want to log failing reqeusts as well in the future
                # right now we only track failures from chat streams and rerank
                # through the decorators
                and response.status_code >= 200
                and response.status_code < 300
            )
            else False
        )

    def _send_signal(
        self, request: Request, response: Response, duration_ms: float, ctx: Context
    ) -> None:
        signal = self._get_event_signal(request, duration_ms, ctx)
        event_type = ctx.get_event_type()
        if self._should_send_signal(signal, event_type, response):
            # signal is being checked in the condition above
            response.background = BackgroundTask(report_metrics, signal, ctx)  # type: ignore

    def _get_event_signal(
        self, request: Request, duration_ms: float, ctx: Context
    ) -> MetricsSignal | None:
        if request.scope["type"] != "http":
            return None

        message_type = ctx.get_event_type()
        if not message_type:
            return None

        logger = ctx.get_logger()

        user = ctx.get_metrics_user()
        # when user is created, user_id is not in the header
        trace_id = ctx.get_trace_id()
        user_id = ctx.get_user_id()
        agent = ctx.get_metrics_agent()
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
                trace_id=trace_id,
                assistant=agent,
                assistant_id=agent_id,
                duration_ms=duration_ms,
            )
            data = self._attach_secret(data)
            signal = MetricsSignal(signal=data)
            return signal
        except Exception as e:
            logger.warning(event=f"[Metrics] Failed to process event data: {e}")
            return None

    def _attach_secret(self, data: MetricsData) -> MetricsData:
        if not REPORT_SECRET:
            return data
        data.secret = REPORT_SECRET
        return data


async def report_metrics(signal: MetricsSignal, ctx: Context) -> None:
    """
    Reports the given metrics signal to the specified endpoint.
    This is the key function for reporting metrics. It should never throw exceptions but log them.

    Args:
        signal (MetricsSignal): The metrics signal to be reported.

    Returns:
        None
    """
    logger = ctx.get_logger()

    if METRICS_LOGS_CURLS == "true":
        MetricsHelper.log_signal_curl(signal, ctx)
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
        logger.error(event=f"[Metrics] Error posting report: {e}")


def collect_metrics_chat_stream(func: Callable) -> Callable:
    """
    Decorator for collecting metrics for chat streams.
    Use with the middleware as needed.
    Args:
        func (Callable): the original function to be decorated, must return an async generator

    Returns:
        Callable: wrapped function that yields the original values

    Yields:
        Iterator[Callable]: the original values from the stream
    """

    @wraps(func)
    async def wrapper(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> Any:
        stream = func(self, chat_request, ctx, **kwargs)
        async for v in stream:
            ChatMetricHelper.report_streaming_chat_event(v, ctx, **kwargs)
            yield v

    return wrapper


def collect_metrics_rerank(func: Callable) -> Callable:
    """
    Decorator for collecting metrics for rerank events.
    Use with the middleware as needed.
    Args:
        func (Callable): function to be decorated

    Raises:
        e: original exception raised by the function

    Returns:
        Callable: the wrapped function
    """

    @wraps(func)
    async def wrapper(
        self, query: str, documents: Dict[str, Any], ctx: Context, **kwargs: Any
    ) -> Any:
        start_time = time.perf_counter()
        try:
            response = await func(self, query, documents, ctx, **kwargs)
            duration_ms = time.perf_counter() - start_time
            RerankMetricsHelper.report_rerank_metrics(
                response, duration_ms, ctx, **kwargs
            )
            return response
        except Exception as e:
            duration_ms = time.perf_counter() - start_time
            RerankMetricsHelper.report_rerank_failed_metrics(
                duration_ms, e, ctx, **kwargs
            )
            raise e

    return wrapper


class MetricsHelper:
    # TODO: remove the logging once metrics are configured correctly
    @staticmethod
    def log_signal_curl(signal: MetricsSignal, ctx: Context) -> None:
        logger = ctx.get_logger()
        s = to_dict(signal)
        s["signal"]["secret"] = "'$SECRET'"
        json_signal = json.dumps(s)
        # just general curl commands to test the endpoint for now
        logger.info(
            event=f"\n\ncurl -X POST -H \"Content-Type: application/json\" -d '{json_signal}' $ENDPOINT\n\n"
        )


# DO NOT THROW EXPCEPTIONS IN THIS FUNCTION
class ChatMetricHelper:
    @staticmethod
    def report_streaming_chat_event(
        event: dict[str, Any], ctx: Context, **kwargs: Any
    ) -> None:
        logger = ctx.get_logger()

        try:
            event_type = event["event_type"]
            if event_type == StreamEvent.STREAM_START:
                ctx.with_stream_start_ms(time.perf_counter())

            if event_type != StreamEvent.STREAM_END:
                return

            duration_ms = None
            time_start = ctx.get_stream_start_ms()
            if time_start:
                duration_ms = time.perf_counter() - time_start
            trace_id = ctx.get_trace_id()
            model = ctx.get_model()
            user_id = ctx.get_user_id()
            agent = ctx.get_metrics_agent()
            agent_id = agent.id if agent else None
            event_dict = to_dict(event).get("response", {})
            input_tokens = (
                event_dict.get("meta", {})
                .get("billed_units", {})
                .get("input_tokens", 0)
            )
            output_tokens = (
                event_dict.get("meta", {})
                .get("billed_units", {})
                .get("output_tokens", 0)
            )
            search_units = (
                event_dict.get("meta", {})
                .get("billed_units", {})
                .get("search_units", 0)
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
            # validate successful event metrics, ignore type errors to rely on pydantic exceptions
            if not is_error:
                MetricsModelAttrs(
                    input_nb_tokens=input_tokens,
                    output_nb_tokens=output_tokens,
                    search_units=search_units,
                    model=model,  # type: ignore
                    assistant_id=agent_id,  # type: ignore
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
            asyncio.create_task(report_metrics(signal, ctx))

        except Exception as e:
            logger.error(event=f"Failed to report streaming event: {e}")


class RerankMetricsHelper:
    # DO NOT THROW EXPCEPTIONS IN THIS FUNCTION
    @staticmethod
    def report_rerank_metrics(
        response: Any, duration_ms: float, ctx: Context, **kwargs: Any
    ):
        logger = ctx.get_logger()

        try:
            (trace_id, model, user_id, agent, agent_id) = (
                RerankMetricsHelper._get_init_data(ctx)
            )
            response_dict = to_dict(response)
            search_units = (
                response_dict.get("meta", {})
                .get("billed_units", {})
                .get("search_units")
            )
            message_type = MetricsMessageType.RERANK_API_SUCCESS
            # ensure valid MetricsChat object
            chat_metrics = MetricsModelAttrs(
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
                input_nb_tokens=0,
                output_nb_tokens=0,
                search_units=search_units,
                timestamp=time.time(),
                duration_ms=duration_ms,
            )
            signal = MetricsSignal(signal=metrics_data)
            asyncio.create_task(report_metrics(signal, ctx))
        except Exception as e:
            logger.error(event=f"[Metrics] Error reporting rerank metrics: {e}")

    @staticmethod
    def report_rerank_failed_metrics(
        duration_ms: float, error: Exception, ctx: Context, **kwargs: Any
    ):
        logger = ctx.get_logger()

        try:
            (trace_id, model, user_id, agent, agent_id) = (
                RerankMetricsHelper._get_init_data(ctx)
            )
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
                duration_ms=duration_ms,
                timestamp=time.time(),
                error=error_message,
            )
            signal = MetricsSignal(signal=metrics_data)
            asyncio.create_task(report_metrics(signal, ctx))
        except Exception as e:
            logger.error(event=f"Failed to report rerank metrics: {e}")

    @staticmethod
    def _get_init_data(ctx: Context) -> tuple:
        trace_id = ctx.get_trace_id()
        model = DEFAULT_RERANK_MODEL
        user_id = ctx.get_user_id()
        agent = ctx.get_metrics_agent()
        agent_id = agent.id if agent else ctx.get_agent_id()
        return (trace_id, model, user_id, agent, agent_id)
