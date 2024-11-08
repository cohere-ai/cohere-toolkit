import asyncio
import itertools
from typing import Any, Callable, Dict, List

from backend.config.settings import Settings
from backend.database_models.database import DBSessionDep
from backend.model_deployments.base import BaseDeployment
from backend.schemas.agent import AgentToolMetadataArtifactsType
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool
from backend.tools.brave_search.tool import BraveWebSearch
from backend.tools.google_search import GoogleWebSearch
from backend.tools.tavily_search import TavilyWebSearch
from backend.tools.utils.mixins import WebSearchFilteringMixin
from backend.tools.web_scrape import WebScrapeTool


class HybridWebSearch(BaseTool, WebSearchFilteringMixin):
    ID = "hybrid_web_search"
    POST_RERANK_MAX_RESULTS = 6
    AVAILABLE_WEB_SEARCH_TOOLS = [TavilyWebSearch, GoogleWebSearch, BraveWebSearch]
    ENABLED_WEB_SEARCH_TOOLS = Settings().get('tools.hybrid_web_search.enabled_web_searches')
    WEB_SCRAPE_TOOL = WebScrapeTool

    def __init__(self):
        available_search_tools = self.get_available_search_tools()

        # Instantiate Search tools and Web scraping tool
        self.search_tools = [search_tool() for search_tool in available_search_tools]
        self.web_scrape_tool = self.WEB_SCRAPE_TOOL()

    @classmethod
    def is_available(cls) -> bool:
        if not cls.ENABLED_WEB_SEARCH_TOOLS:
            return False

        available_searches = cls.get_available_search_tools()

        # False if empty, True otherwise
        return bool(available_searches)

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Hybrid Web Search",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query for retrieval.",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=True,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.WebSearch,
            description=(
                "Returns a list of relevant document snippets for a textual query "
                "retrieved from the internet using a mix of any existing Web Search tools."
            )
        )

    @classmethod
    def get_available_search_tools(cls):
        available_search_tools = []

        for search_name in cls.ENABLED_WEB_SEARCH_TOOLS:
            for search_tool in cls.AVAILABLE_WEB_SEARCH_TOOLS:
                if search_name == search_tool.ID and search_tool.is_available():
                    available_search_tools.append(search_tool)

        return available_search_tools

    def _gather_search_tasks(
        self, parameters: dict, ctx: Any, session: DBSessionDep, **kwargs: Any
    ) -> List[Callable]:
        tasks = []

        # Add search tool calls
        for search_tool in self.search_tools:
            tasks.append(search_tool.call(parameters, ctx, session, **kwargs))

        # Add web scrape tool calls
        filtered_sites = kwargs.get("include_sites", [])
        for site in filtered_sites:
            tasks.append(self.web_scrape_tool.call({"url": site}, ctx, **kwargs))

        return tasks

    async def call(
        self, parameters: dict, ctx: Any, session: DBSessionDep, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        # Retrieve query for reranking
        query = parameters.get("query", "")

        # Handle domain filtering -> filter in search APIs
        filtered_domains = self.get_filters(
            AgentToolMetadataArtifactsType.DOMAIN, session, ctx
        )
        kwargs["include_domains"] = filtered_domains

        # Handle site filtering -> perform web scraping on sites
        filtered_sites = self.get_filters(
            AgentToolMetadataArtifactsType.SITE, session, ctx
        )
        kwargs["include_sites"] = filtered_sites

        tasks = self._gather_search_tasks(parameters, ctx, session, **kwargs)

        # Gather and run searches
        results = await asyncio.gather(*tasks)

        flattened_results = list(itertools.chain.from_iterable(results))

        reranked_results = await self.rerank_results(
            query,
            flattened_results,
            model=kwargs.get("model_deployment"),
            ctx=ctx,
            **kwargs,
        )

        return reranked_results

    async def rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        model: BaseDeployment,
        ctx: Any,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        if not results:
            return []

        rerank_batch_size = 500
        relevance_scores = [None for _ in range(len(results))]
        for batch_start in range(0, len(results), rerank_batch_size):
            results_batch = results[batch_start : batch_start + rerank_batch_size]

            batch_output = await model.invoke_rerank(
                query=query,
                documents=[
                    f"{result.get('title', '')} {result.get('text')}"
                    for result in results_batch
                    if "text" in result
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
            zip(relevance_scores, results), key=lambda x: x[0], reverse=True
        ):
            if result["url"] not in seen_urls:
                seen_urls.append(result["url"])
                reranked.append(result)

        return reranked[: self.POST_RERANK_MAX_RESULTS]
