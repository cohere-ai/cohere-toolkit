from enum import StrEnum
from typing import Any, Dict, List

import backend.crud.file as file_crud
from backend.compass_sdk import SearchFilter
from backend.config.settings import Settings
from backend.schemas.file import File
from backend.services.compass import Compass
from backend.services.file import get_compass
from backend.tools.base import BaseTool


class FileToolsArtifactTypes(StrEnum):
    local_file = "local_file"


def compass_file_search(
    file_ids: List[str],
    conversation_id: str,
    agent_id: str,
    query: str,
    search_limit: int = 5,
) -> List[Dict[str, Any]]:
    results = []

    # Note: Compass search currently has an issue where the type of the context is not directly referenced
    # Temporarily add `.keyword` to workaround this issue.
    search_filters = [
        SearchFilter(
            field="content.file_id.keyword",
            type=SearchFilter.FilterType.EQ,
            value=file_id,
        )
        for file_id in file_ids
    ]

    # Search conversation ID index
    hits = (
        get_compass()
        .invoke(
            action=Compass.ValidActions.SEARCH,
            parameters={
                "index": conversation_id,
                "query": query,
                "top_k": search_limit,
                "filters": search_filters,
            },
        )
        .result["hits"]
    )
    results.extend(hits)

    # Search agent ID index
    if agent_id:
        hits = (
            get_compass()
            .invoke(
                action=Compass.ValidActions.SEARCH,
                parameters={
                    "index": agent_id,
                    "query": query,
                    "top_k": search_limit,
                    "filters": search_filters,
                },
            )
            .result["hits"]
        )
        results.extend(hits)

    chunks = sorted(
        [
            {
                "text": chunk["content"]["text"],
                "score": chunk["score"],
                "url": result["content"].get("title", ""),
                "title": result["content"].get("title", ""),
            }
            for result in results
            for chunk in result["chunks"]
        ],
        key=lambda x: x["score"],
        reverse=True,
    )[:search_limit]

    return chunks


class ReadFileTool(BaseTool):
    """
    This class reads a file from the file system.
    """

    NAME = "read_document"
    MAX_NUM_CHUNKS = 10
    SEARCH_LIMIT = 5

    def __init__(self):
        pass

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        file = parameters.get("file")

        session = kwargs.get("session")
        user_id = kwargs.get("user_id")
        agent_id = kwargs.get("agent_id")
        conversation_id = kwargs.get("conversation_id")
        if not file:
            return []

        _, file_id = file
        if Settings().feature_flags.use_compass_file_storage:
            return compass_file_search(
                [file_id],
                conversation_id,
                agent_id,
                "*",
                search_limit=self.SEARCH_LIMIT,
            )
        else:
            retrieved_file = file_crud.get_file(session, file_id, user_id)
            if not retrieved_file:
                return []

            return [
                {
                    "text": retrieved_file.file_content,
                    "title": retrieved_file.file_name,
                    "url": retrieved_file.file_path,
                }
            ]


class SearchFileTool(BaseTool):
    """
    This class searches for a query in a file.
    """

    NAME = "search_file"
    MAX_NUM_CHUNKS = 10
    SEARCH_LIMIT = 5

    def __init__(self):
        pass

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        query = parameters.get("search_query")
        files = parameters.get("files")

        agent_id = kwargs.get("agent_id")
        conversation_id = kwargs.get("conversation_id")
        session = kwargs.get("session")
        user_id = kwargs.get("user_id")

        if not query or not files:
            return []

        file_ids = [file_id for _, file_id in files]
        if Settings().feature_flags.use_compass_file_storage:
            return compass_file_search(
                file_ids,
                conversation_id,
                agent_id,
                query,
                search_limit=self.SEARCH_LIMIT,
            )
        else:
            retrieved_files = file_crud.get_files_by_ids(session, file_ids, user_id)
            if not retrieved_files:
                return []

            results = []
            for file in retrieved_files:
                results.append(
                    {
                        "text": file.file_content,
                        "title": file.file_name,
                        "url": file.file_path,
                    }
                )
            return results
