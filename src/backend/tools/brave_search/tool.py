from typing import Any, Dict, List

from langchain_community.tools.brave_search.tool import BraveSearch

from backend.config.settings import Settings
from backend.crud import agent_tool_metadata as agent_tool_metadata_crud
from backend.database_models.database import DBSessionDep
from backend.model_deployments.base import BaseDeployment
from backend.schemas.context import Context
from backend.tools.base import BaseTool
from backend.tools.brave_search.client import BraveClient


class BraveWebSearch(BaseTool):
    NAME = "brave_web_search"
    BRAVE_API_KEY = Settings().tools.brave_web_search.api_key

    def __init__(self):
        self.client = BraveClient(api_key=self.BRAVE_API_KEY)
        self.num_results = 20

    @classmethod
    def is_available(cls) -> bool:
        return cls.BRAVE_API_KEY is not None

    def get_filtered_domains(self, session: DBSessionDep, ctx: Context) -> list[str]:
        agent_id = ctx.get_agent_id()
        user_id = ctx.get_user_id()

        if not agent_id or not user_id:
            # Default for Brave is []
            return []

        agent_tool_metadata = agent_tool_metadata_crud.get_agent_tool_metadata(
            db=session,
            agent_id=agent_id,
            tool_name=self.NAME,
            user_id=user_id,
        )

        if not agent_tool_metadata:
            # Default for Brave is []
            return []

        return [
            artifact["domain"]
            for artifact in agent_tool_metadata.artifacts
            if "domain" in artifact
        ]

    async def call(
        self, parameters: dict, ctx: Any, session: DBSessionDep, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")
        filtered_domains = []
        if session:
            filtered_domains = self.get_filtered_domains(session, ctx)

        result = await self.client.search_async(q=query, count=self.num_results, include_domains=filtered_domains)
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

    def to_langchain_tool(self) -> BraveSearch:
        """
        Converts the tool to a Langchain tool.
        """
        brave_search = BraveSearch.from_api_key(
            api_key=self.BRAVE_API_KEY, search_kwargs={"count": self}
        )
        brave_search.name = "brave_web_search"
        brave_search.description = "Returns a list of relevant document snippets for a textual query retrieved from the internet."

        return brave_search
