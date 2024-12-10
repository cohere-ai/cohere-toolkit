from typing import Any, Dict, List

from langchain_community.utilities import ArxivAPIWrapper

from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool


class ArxivRetriever(BaseTool):
    ID = "arxiv"

    def __init__(self):
        self.client = ArxivAPIWrapper()

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Arxiv",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query for retrieval.",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=False,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.DataLoader,
            description="Retrieves documents from Arxiv.",
        )

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")
        try:
            result = self.client.run(query)
        except Exception as e:
            return self.get_tool_error(details=str(e))

        if not result:
            return self.get_no_results_error()

        return [{"text": result}]
