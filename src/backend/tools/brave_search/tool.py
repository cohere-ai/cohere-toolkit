from typing import Any

from backend.config.settings import Settings
from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool, ToolArgument
from backend.tools.brave_search.client import BraveClient


class BraveWebSearch(BaseTool):
    ID = "brave_web_search"
    BRAVE_API_KEY = Settings().get('tools.brave_web_search.api_key')

    def __init__(self):
        self.client = BraveClient(api_key=self.BRAVE_API_KEY)
        self.num_results = 20

    @classmethod
    def is_available(cls) -> bool:
        return cls.BRAVE_API_KEY is not None

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Brave Web Search",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query for retrieval.",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=False,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.WebSearch,
            description=(
                "Returns a list of relevant document snippets for a textual query retrieved "
                "from the internet using Brave Search."
            ),
        ) # type: ignore

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any
    ) -> list[dict[str, Any]]:
        query = parameters.get("query", "")

        # Get domain filtering from kwargs
        filtered_domains = kwargs.get(ToolArgument.DOMAIN_FILTER, [])

        try:
            response = await self.client.search_async(
                q=query, count=self.num_results, include_domains=filtered_domains
            )
        except Exception as e:
            return self.get_tool_error(details=str(e))

        response = dict(response)

        results = response.get("web", {}).get("results", [])

        if not results:
            return self.get_no_results_error()

        tool_results = []
        for result in results:
            tool_results.append({
                "text": result.get("description"),
                "title": result.get("title"),
                "url": result.get("url"),
            })

        return tool_results
