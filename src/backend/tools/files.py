from typing import Any, Dict, List

import backend.crud.file as file_crud
from backend.tools.base import BaseTool
from backend.services.compass import Compass
from backend.services.file import get_file_service

class ReadFileTool(BaseTool):
    """
    This class reads a file from the file system.
    """

    NAME = "read_document"
    MAX_NUM_CHUNKS = 10

    def __init__(self):
        pass

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        files = parameters.get("files", [])
        session = kwargs.get("session")
        user_id = kwargs.get("user_id")

        if not files:
            return []

        # files = file_crud.get_files_by_file_names(session, [file_name], user_id)
        compass = Compass()
        fetched_doc = compass.invoke(
            action=Compass.ValidActions.GET_DOCUMENT,
            parameters={"index": index_name, "file_id": file_id},
        ).result["doc"]["content"]

        if not files:
            return []

        file = files[0]
        return [
            {
                "text": fetched_doc.get("text", ""),
                "title": fetched_doc.get("title", ""),
                "url": fetched_doc.get("url", ""),
            }
        ]


class SearchFileTool(BaseTool):
    """
    This class searches for a query in a file.
    """

    NAME = "search_file"
    MAX_NUM_CHUNKS = 10

    def __init__(self):
        pass

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        query = parameters.get("search_query")
        files = parameters.get("files")
        session = kwargs.get("session")
        user_id = kwargs.get("user_id")

        if not query or not files:
            return []

        # file_names = [
        #     file_name.encode("ascii", "ignore").decode("utf-8")
        #     for file_name in file_names
        # ]

        # files = file_crud.get_files_by_file_names(session, file_names, user_id)
        file_ids = [file_id for file_name, file_id in files]
        files = get_file_service().get_files_by_ids(session, file_ids, user_id)

        if not files:
            return []

        results = []
        for file in files:
            results.append(
                {
                    "text": file.file_content,
                    "title": file.file_name,
                    "url": file.file_path,
                }
            )

        return results
