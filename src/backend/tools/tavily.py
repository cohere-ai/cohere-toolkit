import os, copy
from typing import Any, Dict, List

from langchain_community.tools.tavily_search import TavilySearchResults
from tavily import TavilyClient
from bs4 import BeautifulSoup
from requests import get
from backend.chat.collate import rerank_and_chunk
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
        initial_results = self.client.search(query=query, search_depth="advanced", include_raw_content=True)

        if "results" not in initial_results:
            return []
        
        res = []
        for r in initial_results:
            print(r)
            print("\n\n")
        
        return []

        # results_dict = {result["url"]: result for result in initial_results["results"]}
        # scraped = [self.scrape(link) for link in results_dict]
        # expanded = []
        # for scraped_result in scraped:
        #     initial_result = results_dict[scraped_result["url"]]
        #     expanded.append({
        #         "url": initial_result["url"],
        #         "text": initial_result["content"],
        #     })
            
        #     if scraped_result["title"] is not None:
        #         sentence = f"{scraped_result['title']} {scraped_result['content']}".split("\n")
        #         for snippet in sentence:
        #             if len(snippet) > 20: # Skip short snippets
        #                 expanded.append({
        #                     "url": initial_result["url"],
        #                     "text": snippet.strip(),
        #                 })  

        # return expanded
    
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
                result["link"] not in seen_urls
            ):  # dont return same webpage several times unless allowed
                seen_urls.append(result["link"])
                reranked.append(result)



    
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
