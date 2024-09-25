from typing import Any, Dict, List

from tavily import TavilyClient

from backend.config.settings import Settings
from backend.database_models.database import DBSessionDep
from backend.model_deployments.base import BaseDeployment
from backend.schemas.agent import AgentToolMetadataArtifactsType
from backend.tools.base import BaseTool
from backend.tools.utils.mixins import WebSearchFilteringMixin


class TavilyWebSearch(BaseTool, WebSearchFilteringMixin):
    NAME = "tavily_web_search"
    TAVILY_API_KEY = Settings().tools.tavily_web_search.api_key
    POST_RERANK_MAX_RESULTS = 6

    def __init__(self):
        self.client = TavilyClient(api_key=self.TAVILY_API_KEY)

    @classmethod
    def is_available(cls) -> bool:
        return cls.TAVILY_API_KEY is not None

    async def call(
        self, parameters: dict, ctx: Any, session: DBSessionDep, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        logger = ctx.get_logger()
        # Gather search parameters
        query = parameters.get("query", "")

        # Get domain filtering from kwargs or set on Agent tool metadata
        if "include_domains" in kwargs:
            filtered_domains = kwargs.get("include_domains")
        else:
            filtered_domains = self.get_filters(
                AgentToolMetadataArtifactsType.DOMAIN, session, ctx
            )

        # Do search
        try:
            result = self.client.search(
                query=query,
                search_depth="advanced",
                include_raw_content=True,
                include_domains=filtered_domains,
            )
        except Exception as e:
            logger.error(f"Failed to perform Tavily web search: {str(e)}")
            raise Exception(f"Failed to perform Tavily web search: {str(e)}")

        if "results" not in result:
            return [{"No web results found"}]

        expanded = []
        for result in result["results"]:
            # Append original search result
            expanded.append(result)

            # Get other snippets
            snippets = result["raw_content"].split("\n")
            for snippet in snippets:
                if result["content"] != snippet:
                    if len(snippet.split()) <= 10:
                        continue  # Skip snippets with less than 10 words

                    new_result = {
                        "url": result["url"],
                        "title": result["title"],
                        "content": snippet.strip(),
                    }
                    expanded.append(new_result)

        reranked_results = await self.rerank_page_snippets(
            query, expanded, model=kwargs.get("model_deployment"), ctx=ctx, **kwargs
        )

        return [
            {"url": result["url"], "text": result["content"], "title": result["title"]}
            for result in reranked_results
        ]

    async def rerank_page_snippets(
        self,
        query: str,
        snippets: List[Dict[str, Any]],
        model: BaseDeployment,
        ctx: Any,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        if len(snippets) == 0:
            return []

        rerank_batch_size = 500
        relevance_scores = [None for _ in range(len(snippets))]
        for batch_start in range(0, len(snippets), rerank_batch_size):
            snippet_batch = snippets[batch_start : batch_start + rerank_batch_size]
            batch_output = await model.invoke_rerank(
                query=query,
                documents=[
                    f"{snippet['title']} {snippet['content']}"
                    for snippet in snippet_batch
                ],
                ctx=ctx,
            )
            for b in batch_output.get("results", []):
                index = b.get("index", None)
                relevance_score = b.get("relevance_score", None)
                if index is not None:
                    relevance_scores[batch_start + index] = relevance_score

        reranked, seen_urls = [], []
        for _, result in sorted(
            zip(relevance_scores, snippets), key=lambda x: x[0], reverse=True
        ):
            if result["url"] not in seen_urls:
                seen_urls.append(result["url"])
                reranked.append(result)

        return reranked[: self.POST_RERANK_MAX_RESULTS]
