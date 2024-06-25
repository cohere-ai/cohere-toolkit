import os, copy
from typing import Any, Dict, List

from langchain_community.tools.tavily_search import TavilySearchResults
from tavily import TavilyClient
from backend.model_deployments.base import BaseDeployment

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
        result = self.client.search(query=query, search_depth="advanced", include_raw_content=True)

        if "results" not in result:
            return []

        expanded = []
        for result in result["results"]:
            # Append original search result
            expanded.append(result)

            # Get other snippets
            snippets = result["raw_content"].split("\n")
            for snippet in snippets:
                if result["content"] != snippet:
                    if len(snippet.split()) > 10: # Skip snippets with less than 10 words
                        new_result = {
                            "url": result["url"],
                            "title": result["title"],
                            "content": snippet.strip()
                        }
                        expanded.append(new_result)

        reranked_results = self.rerank_page_results(
            query,
            expanded,
            allow_duplicate_urls=False,
            use_title=True,
            model=kwargs.get("model_deployment")
        )

        return [
            {
                "url": result["url"],
                "text": result["content"]
            } 
            for result in reranked_results
        ]

    
    def rerank_page_results(self, query: str, snippets: List[Dict[str, Any]], allow_duplicate_urls: bool, use_title: bool, model: BaseDeployment) -> List[Dict[str, Any]]:
        if len(snippets) == 0:
            return []
        
        rerank_batch_size = 500
        relevance_scores = [None for _ in range(len(snippets))]
        for batch_start in range(0, len(snippets), rerank_batch_size):
            snippet_batch = snippets[batch_start: batch_start+rerank_batch_size]
            if use_title:
                batch_output = model.invoke_rerank(
                    query=query,
                    documents=[f"{snippet['title']} {snippet['content']}" for snippet in snippet_batch],
                )
            else:
                batch_output = model.invoke_rerank(
                    query=query,
                    documents=[snippet["content"] for snippet in snippet_batch],
                )
            for b in batch_output.results:
                relevance_scores[batch_start + b.index] = b.relevance_score

        reranked, seen_urls = [], []
        for _, result in sorted(zip(relevance_scores, snippets), key=lambda x: -x[0]):
            if allow_duplicate_urls or (
                result["url"] not in seen_urls
            ):  # dont return same webpage several times unless allowed
                seen_urls.append(result["url"])
                reranked.append(result)
        
        for r in reranked:
            print(r)
            print("\n\n")
        return reranked


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
