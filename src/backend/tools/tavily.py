import os
from typing import Any, Dict, List

from langchain_community.tools.tavily_search import TavilySearchResults
from tavily import TavilyClient

from backend.tools.base import BaseTool


class TavilyInternetSearch(BaseTool):
    tavily_api_key = os.environ.get("TAVILY_API_KEY")

    def __init__(self):
        self.client = TavilyClient(api_key=self.tavily_api_key)

    @classmethod
    def is_available(cls) -> bool:
        return cls.tavily_api_key is not None

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")
        content = self.client.search(query=query, search_depth="advanced")

        if "results" not in content:
            return []

        return [
            {
                "url": result["url"],
                "text": result["content"],
            }
            for result in content["results"]
        ]

    def to_langchain_tool(self) -> TavilySearchResults:
        internet_search = TavilySearchResults()
        internet_search.name = "internet_search"
        internet_search.description = "Returns a list of relevant document snippets for a textual query retrieved from the internet."

        # pydantic v1 base model
        from langchain_core.pydantic_v1 import BaseModel, Field

        class TavilySearchInput(BaseModel):
            query: str = Field(description="Query to search the internet with")

        internet_search.args_schema = TavilySearchInput

        return internet_search
