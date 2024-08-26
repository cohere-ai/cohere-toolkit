from typing import Any, Dict, List

from backend.config.settings import Settings
from backend.crud import agent_tool_metadata as agent_tool_metadata_crud
from backend.database_models.database import DBSessionDep
from backend.schemas.context import Context
from backend.tools.base import BaseTool
from backend.tools import (
    TavilyWebSearch,
    GoogleWebSearch,
    BraveWebSearch,
)


class HybridWebSearch(BaseTool):
    NAME = "hybrid_web_search"
    AVAILABLE_WEB_SEARCH_IMPLEMENTATIONS = [TavilyWebSearch, GoogleWebSearch, BraveWebSearch]
    ENABLED_WEB_SEARCHES = Settings().tools.hybrid_web_search.enabled_web_searches

    def __init__(self):
        pass

    @classmethod
    def is_available(cls) -> bool:
        if not cls.ENABLED_WEB_SEARCHES:
            return False 
        
        return True

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
        filtered_domains = self.get_filtered_domains(session, ctx)

        # Combine filters
    
        return tool_results
