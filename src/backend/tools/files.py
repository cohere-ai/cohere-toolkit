from typing import Any, Dict, List

import backend.crud.file as file_crud
from backend.config.settings import Settings
from backend.services.compass import Compass
from backend.services.file import get_file_service
from backend.tools.base import BaseTool


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

        if Settings().feature_flags.use_compass_file_storage:
            file_ids = [file_id for _, file_id in files]
            files = get_file_service().get_files_by_ids(session, file_ids, user_id)
        else:
            # TODO get file by file id not file name
            files = file_crud.get_files_by_file_names(session, file_names, user_id)

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

        files = []
        if Settings().feature_flags.use_compass_file_storage:
            file_ids = [file_id for _, file_id in files]
            files = get_file_service().get_files_by_ids(session, file_ids, user_id)
        else:
            # TODO get file by file id not file name
            file_names = [file_name for file_name, _ in files]
            files = file_crud.get_files_by_file_names(session, file_names, user_id)

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
