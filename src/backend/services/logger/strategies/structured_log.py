import structlog

from backend.schemas.context import Context
from backend.services.logger.strategies.base import BaseLogger


def log_context(func):
    def wrapper(self, **kwargs):
        ctx = kwargs.get("ctx")
        if ctx:
            kwargs["ctx"] = get_context_log(ctx)
        return func(self, **kwargs)

    return wrapper


def get_context_log(ctx: Context) -> dict:
    """
    Remove private attributes from context and return a dictionary.
    """
    ctx.request = None
    ctx.response = None
    ctx.receive = None
    ctx_dict = ctx.model_dump()

    return ctx_dict


class StructuredLogging(BaseLogger):
    def __init__(self, level: str = "info"):
        structlog.configure(
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer("msg"),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(level),
            cache_logger_on_first_use=True,  # Remove this line to make changes to the logger
        )

        self.setup()

        self.logger = structlog.get_logger()

    def setup(self):
        structlog.contextvars.clear_contextvars()

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

    def bind(self, **kwargs):
        self.logger = self.logger.bind(**kwargs)
