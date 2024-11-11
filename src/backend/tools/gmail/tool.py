from typing import Any, Dict, List

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseTool
from backend.tools.gmail.auth import GmailAuth
from backend.tools.gmail.constants import GMAIL_TOOL_ID, SEARCH_LIMIT
from backend.tools.gmail.utils import get_gmail_service

logger = LoggerFactory().get_logger()


class GmailTool(BaseTool):
    """
    Tool that searches Gmail for messages and files based on a query.
    """

    ID = GMAIL_TOOL_ID
    CLIENT_ID = ""
    CLIENT_SECRET = ""

    @classmethod
    def is_available(cls) -> bool:
        settings = Settings()
        gmail_settings = settings.tools.gmail if settings.tools and settings.tools.gmail else None
        cls.CLIENT_ID = getattr(gmail_settings, 'client_id', None)
        cls.CLIENT_SECRET = getattr(gmail_settings, 'client_secret', None)

        return cls.CLIENT_ID is not None and cls.CLIENT_SECRET is not None

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Gmail",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query to search Gmail.",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=True,
            is_available=cls.is_available(),
            auth_implementation=GmailAuth,
            error_message=cls.generate_error_message(),
            category=ToolCategory.DataLoader,
            description="Returns a list of relevant email snippets from Gmail.",
        )

    @classmethod
    def _handle_tool_specific_errors(cls, error: Exception, **kwargs: Any) -> None:
        message = "[Gmail] Tool Error: {}".format(str(error))

        if error:
            session = kwargs["session"]
            user_id = kwargs["user_id"]
            tool_auth_crud.delete_tool_auth(
                db=session, user_id=user_id, tool_id=GMAIL_TOOL_ID
            )

        logger.error(
            event="[Gmail] Auth token error: Please refresh the page and re-authenticate."
        )
        raise Exception(message)

    async def call(self, parameters: dict, ctx: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        user_id = kwargs.get("user_id", "")
        query = parameters.get("query", "")

        gmail_service = get_gmail_service(user_id=user_id, search_limit=SEARCH_LIMIT)
        results = gmail_service.search_all(query=query)
        message_ids = [message["id"] for message in results["messages"]] if "messages" in results else []
        messages = gmail_service.retrieve_messages(message_ids)
        return gmail_service.serialize_results(messages)
