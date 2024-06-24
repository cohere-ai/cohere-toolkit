import os, copy
from typing import Any, Dict, List

from langchain_community.tools.tavily_search import TavilySearchResults
from tavily import TavilyClient
from bs4 import BeautifulSoup
from requests import get

from backend.tools.base import BaseTool


class TavilyInternetSearch(BaseTool):
    NAME = "web_search"
    TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

    def __init__(self):
        self.client = TavilyClient(api_key=self.TAVILY_API_KEY)

    @classmethod
    def is_available(cls) -> bool:
        return cls.TAVILY_API_KEY is not None

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")
        initial_results = self.client.search(query=query, search_depth="advanced")

        if "results" not in initial_results:
            return []

        results_dict = {result["url"]: result for result in initial_results["results"]}
        scraped = [self.scrape(link) for link in results_dict]
        expanded = []
        for scraped_result in scraped:
            initial_result = results_dict[scraped_result["url"]]
            expanded.append({
                "url": initial_result["url"],
                "text": initial_result["content"],
            })
            
            if scraped_result["title"] is not None:
                sentence = f"{scraped_result['title']} {scraped_result['content']}".split("\n")
                for snippet in sentence:
                    if len(snippet) > 20: # Skip short snippets
                        expanded.append({
                            "url": initial_result["url"],
                            "text": snippet.strip(),
                        })  

        return expanded
    
    def scrape(self, url: str) -> Dict[str, Any]:
        response = get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        return {
            "url": url,
            "title": soup.title.text if soup.title else None,
            "content": ' '.join([p.text for p in soup.find_all('p')])
        }

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
