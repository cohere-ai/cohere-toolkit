from typing import Any

from tavily import TavilyClient

from backend.config.settings import Settings
from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool, ToolArgument


class TavilyWebSearch(BaseTool):
    ID = "tavily_web_search"
    TAVILY_API_KEY = Settings().get('tools.tavily_web_search.api_key')

    def __init__(self):
        self.client = TavilyClient(api_key=self.TAVILY_API_KEY)

    @classmethod
    def is_available(cls) -> bool:
        return cls.TAVILY_API_KEY is not None

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Web Search",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query to search the internet with",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=False,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.WebSearch,
            description="Returns a list of relevant document snippets for a textual query retrieved from the internet.",
        ) # type: ignore

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any,
    ) -> list[dict[str, Any]]:
        logger = ctx.get_logger()
        # Gather search parameters
        query = parameters.get("query", "")

        # Get domain filtering from kwargs
        filtered_domains = kwargs.get(ToolArgument.DOMAIN_FILTER, [])

        try:
            result = self.client.search(
                query=query,
                search_depth="advanced",
                include_raw_content=True,
                include_domains=filtered_domains,
            )
        except Exception as e:
            logger.error(f"Failed to perform Tavily web search: {str(e)}")
            return self.get_tool_error(details=str(e))

        results = result.get("results", [])

        if not results:
            return self.get_no_results_error()

        tool_results = []
        for result in results:
            # Retrieve snippets from raw content if exists
            raw_content = result.get("raw_content")
            if raw_content:
                # Get other snippets
                snippets = raw_content.split("\n")
                for snippet in snippets:
                    if result.get("content") != snippet:
                        if len(snippet.split()) <= 10:
                            continue  # Skip snippets with less than 10 words

                        tool_results.append({
                            "text": snippet.strip(),
                            "title": result.get("title"),
                            "url": result.get("url"),
                        })

        return tool_results
