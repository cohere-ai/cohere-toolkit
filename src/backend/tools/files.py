from typing import Any, Dict, List

from pypdf import PdfReader

import backend.crud.file as file_crud
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

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        file_name = parameters.get("filename", "")
        session = kwargs.get("session")
        user_id = kwargs.get("user_id")

        if not file_name:
            return []

        files = file_crud.get_files_by_file_names(session, [file_name], user_id)

        if not files:
            return []

        file = files[0]
        return [
            {
                "text": file.file_content,
                "title": file.file_name,
                "url": file.file_path,
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

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        query = parameters.get("search_query")
        file_names = parameters.get("filenames")
        model_deployment = kwargs.get("model_deployment")
        session = kwargs.get("session")
        user_id = kwargs.get("user_id")

        if not query or not file_names:
            return []

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


def get_file_content(file_path):
    # Currently only supports PDF files
    loader = PdfReader(file_path)
    text = ""
    for page in loader.pages:
        text += page.extract_text() + "\n"

    return text
