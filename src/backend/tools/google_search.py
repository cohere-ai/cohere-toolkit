from typing import Any

from googleapiclient.discovery import build

from backend.config.settings import Settings
from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool, ToolArgument


class GoogleWebSearch(BaseTool):
    ID = "google_web_search"
    API_KEY = Settings().get('tools.google_web_search.api_key')
    CSE_ID = Settings().get('tools.google_web_search.cse_id')

    def __init__(self):
        self.client = build("customsearch", "v1", developerKey=self.API_KEY)

    @classmethod
    def is_available(cls) -> bool:
        return bool(cls.API_KEY) and bool(cls.CSE_ID)

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Google Web Search",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "A search query for the Google search engine.",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=False,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.WebSearch,
            description="Returns relevant results by performing a Google web search.",
        ) # type: ignore

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any,
    ) -> list[dict[str, Any]]:
        query = parameters.get("query", "")
        cse = self.client.cse()

        # Get domain filtering from kwargs
        filtered_domains = kwargs.get(ToolArgument.DOMAIN_FILTER, [])
        domain_filters = [f"site:{domain}" for domain in filtered_domains]
        try:
            response = cse.list(q=query, cx=self.CSE_ID, orTerms=domain_filters).execute()
            search_results = response.get("items", [])
        except Exception as e:
            return self.get_tool_error(details=str(e))

        if not search_results:
            return self.get_no_results_error()

        tool_results = []
        for result in search_results:
            if "snippet" not in result:
                continue

            tool_results.append({
                "text": result.get("snippet"),
                "title": result.get("title"),
                "url": result.get("url")
            })

        return tool_results
