import time
from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from backend.config.settings import Settings
from backend.crud import tool_auth as tool_auth_crud
from backend.services.compass import Compass
from backend.services.logger.utils import LoggerFactory
from backend.tools.base import BaseTool

from .constants import (
    GOOGLE_MAIL_TOOL_ID,
    SEARCH_LIMIT,
)

logger = LoggerFactory().get_logger()


class GoogleMail(BaseTool):
    """
    Tool that searches Google Mail
    """

    NAME = GOOGLE_MAIL_TOOL_ID

    CLIENT_ID = Settings().tools.google_drive.client_id
    CLIENT_SECRET = Settings().tools.google_drive.client_secret
    compass: Optional[Compass] = None

    @classmethod
    def is_available(cls) -> bool:
        return cls.CLIENT_ID is not None and cls.CLIENT_ID is not None

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        session = kwargs.get("session")
        user_id = kwargs.get("user_id")
        agent_id = kwargs["agent_id"]
        if not agent_id:
            error_message = f"[Google Mail] Must have an agent_id to search Google Mail"
            logger.error(event=error_message)
            raise HTTPException(status_code=401, detail=error_message)

        query = parameters.get("query", "").replace("'", "\\'")
        tool_auth = tool_auth_crud.get_tool_auth(
            db=session, tool_id=GOOGLE_MAIL_TOOL_ID, user_id=user_id
        )
        if not tool_auth:
            error_message = f"[Google Mail] Error searching Google Mail: Could not find ToolAuth with tool_id: {self.NAME} and user_id: {kwargs.get('user_id')}"
            logger.error(event=error_message)
            return []

        # init compass
        try:
            self.compass = Compass()
        except Exception as e:
            error_message = f"[Google mail] cannot init compass with tool_id: {self.NAME} and user_id: {kwargs.get('user_id')}"
            logger.error(event=error_message)
            logger.error(event=e)
            return []
        # ensure index exists
        index_name = "{}_{}".format(agent_id, GOOGLE_MAIL_TOOL_ID)
        # TODO: remove this hard coded index name!!!!
        index_name = "gmail_tanzim_test"
        if self.compass.has_index(index_name):
            return self._query_compass(index_name, query)
        logger.warning(
            event=f"[Google Mail] Error searching Google Mail: Index {index_name} does not exist yet!"
        )
        return []

    def _query_compass(
        self, index_name: str, query: str, top_k=SEARCH_LIMIT
    ) -> List[Dict[str, Any]]:
        hits = self.compass.invoke(
            action=Compass.ValidActions.SEARCH,
            parameters={
                "index": index_name,
                "query": query,
                "top_k": top_k,
            },
        ).result["hits"]
        chunks = sorted(
            [
                {
                    "text": chunk["content"]["text"],
                    "score": chunk["score"],
                    "title": hit["content"].get("title", ""),
                }
                for hit in hits
                for chunk in hit["chunks"]
            ],
            key=lambda x: x["score"],
            reverse=True,
        )[:top_k]

        return chunks
