from typing import Any, Dict, List

from langchain_community.document_loaders import PyPDFLoader

import backend.crud.file as file_crud
from backend.tools.base import BaseTool


class ReadFileTool(BaseTool):
    """
    This class reads a file from the file system.
    """

    def __init__(self, file_path: str):
        pass

    @classmethod
    def is_available(cls) -> bool:
        return True

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        file_name = parameters.get("file_name", "")
        if not file_name:
            return []

        file = file_crud.get_file_by_file_name(file_name)
        return [
            {
                "text": file.file_content,
                "title": file.file_name,
                "url": file.file_path,
            }
        ]


def get_file_content(file_path):
    # Currently only supports PDF files
    loader = PyPDFLoader(file_path)
    return loader.get_text()
