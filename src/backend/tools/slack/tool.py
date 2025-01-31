from typing import Any

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseTool
from backend.tools.slack.auth import SlackAuth
from backend.tools.slack.constants import SEARCH_LIMIT, SLACK_TOOL_ID
from backend.tools.slack.utils import get_slack_service

logger = LoggerFactory().get_logger()


class SlackTool(BaseTool):
    """
    Tool that searches Slack for messages and files based on a query.
    """

    ID = SLACK_TOOL_ID
    CLIENT_ID = Settings().get('tools.slack.client_id')
    CLIENT_SECRET = Settings().get('tools.slack.client_secret')

    @classmethod
    def is_available(cls) -> bool:
        return cls.CLIENT_ID is not None and cls.CLIENT_SECRET is not None

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Slack",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query to search slack.",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=True,
            is_available=cls.is_available(),
            auth_implementation=SlackAuth,
            should_return_token=False,
            error_message=cls.generate_error_message(),
            category=ToolCategory.DataLoader,
            description="Returns a list of relevant document snippets from slack.",
        ) # type: ignore

    @classmethod
    def _handle_tool_specific_errors(cls, error: Exception, **kwargs: Any) -> None:
        message = "[Slack] Tool Error: {}".format(str(error))

        if error:
            session = kwargs["session"]
            user_id = kwargs["user_id"]
            tool_auth_crud.delete_tool_auth(
                db=session, user_id=user_id, tool_id=SLACK_TOOL_ID
            )

        logger.error(
            event="[Slack] Auth token error: Please refresh the page and re-authenticate."
        )
        raise Exception(message)

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any,
    ) -> list[dict[str, Any]]:
        user_id = kwargs.get("user_id", "")
        query = parameters.get("query", "")

        # Search Slack
        slack_service = get_slack_service(user_id=user_id, search_limit=SEARCH_LIMIT)
        try:
            all_results = slack_service.search_all(query=query)
            results = slack_service.serialize_results(all_results)
        except Exception as e:
            return self.get_tool_error(details=str(e))

        if not results:
            return self.get_no_results_error()

        return results

