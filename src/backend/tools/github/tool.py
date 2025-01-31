from typing import Any

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseTool
from backend.tools.github.auth import GithubAuth
from backend.tools.github.constants import GITHUB_TOOL_ID, SEARCH_LIMIT
from backend.tools.github.utils import get_github_service

logger = LoggerFactory().get_logger()


class GithubTool(BaseTool):
    """
    Tool that searches Github for repositories based on a query.
    """
    ID = GITHUB_TOOL_ID
    CLIENT_ID = Settings().get('tools.github.client_id')
    CLIENT_SECRET = Settings().get('tools.github.client_secret')
    DEFAULT_REPOS = Settings().get('tools.github.default_repos')

    @classmethod
    def is_available(cls) -> bool:
        return cls.CLIENT_ID is not None and cls.CLIENT_SECRET is not None

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Github",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query to search Github.",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=True,
            is_available=cls.is_available(),
            auth_implementation=GithubAuth,
            should_return_token=False,
            error_message=cls.generate_error_message(),
            category=ToolCategory.DataLoader,
            description="Returns a list of relevant document snippets from Github.",
        ) # type: ignore

    @classmethod
    def _handle_tool_specific_errors(cls, error: Exception, **kwargs: Any) -> None:
        message = "[Github] Tool Error: {}".format(str(error))

        if error:
            session = kwargs["session"]
            user_id = kwargs["user_id"]
            tool_auth_crud.delete_tool_auth(
                db=session, user_id=user_id, tool_id=GITHUB_TOOL_ID
            )

        logger.error(
            event="[Github] Auth token error: Please refresh the page and re-authenticate."
        )
        raise Exception(message)

    async def call(self, parameters: dict, ctx: Context, **kwargs: Any) -> list[dict[str, Any]]:
        user_id = kwargs.get("user_id", "")
        query = parameters.get("query", "")

        # Search Slack
        github_service = get_github_service(user_id=user_id, default_repos=self.DEFAULT_REPOS,
                                            search_limit=SEARCH_LIMIT)
        try:
            all_results = github_service.search(query=query)
            results = github_service.transform_response(all_results)
        except Exception as e:
            return self.get_tool_error(details=str(e))

        if not results:
            return self.get_no_results_error()

        return results
