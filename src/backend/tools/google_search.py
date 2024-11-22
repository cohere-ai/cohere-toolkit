from typing import Any, Dict, List

from googleapiclient.discovery import build

from backend.config.settings import Settings
from backend.database_models.database import DBSessionDep
from backend.schemas.agent import AgentToolMetadataArtifactsType
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool
from backend.tools.utils.mixins import WebSearchFilteringMixin


class GoogleWebSearch(BaseTool, WebSearchFilteringMixin):
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
        )

    async def call(
        self, parameters: dict, ctx: Any, session: DBSessionDep, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")
        cse = self.client.cse()

        # Get domain filtering from kwargs or set on Agent tool metadata
        if "include_domains" in kwargs:
            filtered_domains = kwargs.get("include_domains")
        else:
            filtered_domains = self.get_filters(
                AgentToolMetadataArtifactsType.DOMAIN, session, ctx
            )

        site_filters = [f"site:{domain}" for domain in filtered_domains]
        response = cse.list(q=query, cx=self.CSE_ID, orTerms=site_filters).execute()
        search_results = response.get("items", [])

        tool_results = []
        for result in search_results:
            tool_result = {
                "title": result["title"],
                "url": result["link"],
            }
            if "snippet" in result:
                tool_result["text"] = result["snippet"]
            tool_results.append(tool_result)

        return tool_results
