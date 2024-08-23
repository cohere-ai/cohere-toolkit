from typing import Any, Dict, List

from googleapiclient.discovery import build

from backend.config.settings import Settings
from backend.crud import agent_tool_metadata as agent_tool_metadata_crud
from backend.database_models.database import DBSessionDep
from backend.schemas.context import Context
from backend.tools.base import BaseTool


class GoogleWebSearch(BaseTool):
    NAME = "google_web_search"
    API_KEY = Settings().tools.google_web_search.api_key
    CSE_ID = Settings().tools.google_web_search.cse_id

    def __init__(self):
        self.client = build("customsearch", "v1", developerKey=self.API_KEY)

    @classmethod
    def is_available(cls) -> bool:
        return bool(cls.API_KEY) and bool(cls.CSE_ID)

    def get_filtered_domains(self, session: DBSessionDep, ctx: Context) -> list[str]:
        agent_id = ctx.get_agent_id()
        user_id = ctx.get_user_id()

        if not agent_id or not user_id:
            return []

        agent_tool_metadata = agent_tool_metadata_crud.get_agent_tool_metadata(
            db=session,
            agent_id=agent_id,
            tool_name=self.NAME,
            user_id=user_id,
        )

        if not agent_tool_metadata:
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
        cse = self.client.cse()
        filtered_domains = self.get_filtered_domains(session, ctx)
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
