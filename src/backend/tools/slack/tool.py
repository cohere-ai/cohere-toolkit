from typing import Any, Dict, List

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseTool
from backend.tools.slack.constants import SEARCH_LIMIT, SLACK_TOOL_ID
from backend.tools.slack.utils import get_slack_service

logger = LoggerFactory().get_logger()


class SlackTool(BaseTool):
    """
    Tool that searches Slack
    """

    NAME = SLACK_TOOL_ID
    CLIENT_ID = ""
    CLIENT_SECRET = ""

    @classmethod
    def is_available(cls) -> bool:
        settings = Settings()
        cls.CLIENT_ID = settings.tools.slack.client_id if settings.tools and settings.tools.slack and settings.tools.slack.client_id else None
        cls.CLIENT_SECRET = settings.tools.slack.client_secret if settings.tools and settings.tools.slack and settings.tools.slack.client_secret else None

        return cls.CLIENT_ID is not None and cls.CLIENT_SECRET is not None

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

    async def call(self, parameters: dict, ctx: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        user_id = kwargs.get("user_id", "")
        query = parameters.get("query", "")

        # Search Slack
        slack_service = get_slack_service(user_id=user_id, search_limit=SEARCH_LIMIT)
        all_results = slack_service.search_all(query=query)
        return slack_service.serialize_results(all_results)

