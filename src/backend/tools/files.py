from enum import StrEnum
from typing import Any

import backend.crud.file as file_crud
from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool


class FileToolsArtifactTypes(StrEnum):
    local_file = "file"

class ReadFileTool(BaseTool):
    """
    Tool to read a file from the file system.
    """

    ID = "read_file"
    MAX_NUM_CHUNKS = 10
    SEARCH_LIMIT = 5

    def __init__(self):
        pass

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Read Document",
            implementation=cls,
            parameter_definitions={
                "file": {
                    "description": "A file represented as a tuple (filename, file ID) to read over",
                    "type": "tuple[str, str]",
                    "required": True,
                }
            },
            is_visible=True,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.FileLoader,
            description="Returns the chunked textual contents of an uploaded file.",
        ) # type: ignore

    @classmethod
    def get_info(cls) -> ToolDefinition:
        return ToolDefinition(
            display_name="Calculator",
            description="A powerful multi-purpose calculator capable of a wide array of math calculations.",
            error_message=cls.generate_error_message(),
        ) # type: ignore

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any,
    ) -> list[dict[str, Any]]:
        file = parameters.get("file")

        session = kwargs.get("session")
        user_id = kwargs.get("user_id")
        if not file:
            return self.get_tool_error(details="Files are not passed in model generated params")

        _, file_id = file
        retrieved_file = file_crud.get_file(session, file_id, user_id)
        if not retrieved_file:
            return self.get_tool_error(details="The wrong files were passed in the tool parameters, or files were not found")

        return [
            {
                "text": retrieved_file.file_content,
                "title": retrieved_file.file_name,
                "url": retrieved_file.file_name,
            }
        ]

class SearchFileTool(BaseTool):
    """
    Tool to query a list of files.
    """

    ID = "search_file"
    DISPLAY_NAME = "Search Files"
    MAX_NUM_CHUNKS = 10
    SEARCH_LIMIT = 5

    def __init__(self):
        pass

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Search File",
            implementation=cls,
            parameter_definitions={
                "search_query": {
                    "description": "Textual search query to search over the file's content for",
                    "type": "str",
                    "required": True,
                },
                "files": {
                    "description": "A list of files represented as tuples of (filename, file ID) to search over",
                    "type": "list[tuple[str, str]]",
                    "required": True,
                },
            },
            is_visible=True,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.FileLoader,
            description="Searches across one or more attached files based on a textual search query.",
        ) # type: ignore

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any,
    ) -> list[dict[str, Any]]:
        query = parameters.get("search_query")
        files = parameters.get("files")

        session = kwargs.get("session")
        user_id = kwargs.get("user_id", "")

        if not query or not files:
            return self.get_tool_error(
                details="Missing query or files. The wrong files might have been passed in the tool parameters")

        file_ids = [file_id for _, file_id in files]
        retrieved_files = file_crud.get_files_by_ids(session, file_ids, user_id)

        if not retrieved_files:
            return self.get_tool_error(
                details="Missing files. The wrong files might have been passed in the tool parameters")

        results = []
        for file in retrieved_files:
            results.append(
                {
                    "text": file.file_content,
                    "title": file.file_name,
                    "url": file.file_name,
                }
            )
        if not results:
            return self.get_no_results_error()

        return results
