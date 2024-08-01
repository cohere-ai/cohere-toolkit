import logging
from typing import Any, Dict

import structlog

from backend.services.logger.strategies.base import BaseLogger


def log_context(func):
    def wrapper(self, **kwargs):
        ctx = kwargs.get("ctx")
        if ctx:
            kwargs["ctx"] = get_context_log(ctx)
        return func(self, **kwargs)

    return wrapper


def get_context_log(ctx: Any) -> dict:
    """
    Remove private attributes from context and return a dictionary.
    """
    ctx_dict = ctx.model_dump()

    keys_to_remove = ["request", "response", "receive", "logger"]
    for key in keys_to_remove:
        ctx_dict.pop(key, None)

    return ctx_dict


def add_module(
    logger: structlog.BoundLogger, name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    _, module_str = structlog._frames._find_first_app_frame_and_name(
        additional_ignores=[__name__]
    )
    event_dict["module"] = module_str
    return event_dict


class StructuredLogging(BaseLogger):
    def __init__(self, level: str = "info", renderer: str = "json"):
        self.setup(level, renderer)
        self.logger = structlog.get_logger()

    def setup(self, level: str = "info", renderer: str = "json"):
        level = getattr(logging, level.upper(), None)

        structlog.contextvars.clear_contextvars()

        shared_processors = [
            structlog.processors.add_log_level,
            add_module,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
        ]

        # If running in a terminal, use colored output
        # Otherwise, use JSON output
        if renderer.lower() == "console":
            processors = shared_processors + [
                structlog.dev.set_exc_info,
                structlog.dev.ConsoleRenderer(),
            ]
        else:
            processors = shared_processors + [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ]

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(level),
            cache_logger_on_first_use=True,  # Remove this line to make changes to the logger
        )

    @log_context
    def info(self, **kwargs):
        self.logger.info(**kwargs)

    @log_context
    def error(self, **kwargs):
        self.logger.error(**kwargs)

    @log_context
    def warning(self, **kwargs):
        self.logger.warning(**kwargs)

    @log_context
    def debug(self, **kwargs):
        self.logger.debug(**kwargs)

    @log_context
    def critical(self, **kwargs):
        self.logger.critical(**kwargs)

    @log_context
    def exception(self, **kwargs):
        self.logger.exception(**kwargs)

    @log_context
    def bind(self, **kwargs):
        self.logger = self.logger.bind(**kwargs)

    def unbind(self, *args):
        self.logger = self.logger.unbind(*args)
