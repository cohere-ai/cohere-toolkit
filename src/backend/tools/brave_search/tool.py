from typing import Any, Dict, List

from backend.config.settings import Settings
from backend.database_models.database import DBSessionDep
from backend.model_deployments.base import BaseDeployment
from backend.schemas.agent import AgentToolMetadataArtifactsType
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool
from backend.tools.brave_search.client import BraveClient
from backend.tools.utils.mixins import WebSearchFilteringMixin


class BraveWebSearch(BaseTool, WebSearchFilteringMixin):
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
        )

    async def call(
        self, parameters: dict, ctx: Any, session: DBSessionDep, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")

        # Get domain filtering from kwargs or set on Agent tool metadata
        if "include_domains" in kwargs:
            filtered_domains = kwargs.get("include_domains")
        else:
            filtered_domains = self.get_filters(
                AgentToolMetadataArtifactsType.DOMAIN, session, ctx
            )

        result = await self.client.search_async(
            q=query, count=self.num_results, include_domains=filtered_domains
        )
        result = dict(result)

        if "web" not in result and "results" not in result["web"]:
            return []

        transformed_results = []
        for item in result["web"]["results"]:
            new_result = {
                "url": item["url"],
                "title": item["title"],
                "content": item["description"],
            }
            transformed_results.append(new_result)

        reranked_results = await self.rerank_page_snippets(
            query,
            transformed_results,
            model=kwargs.get("model_deployment"),
            ctx=ctx,
            **kwargs,
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

        return reranked[: self.num_results]
