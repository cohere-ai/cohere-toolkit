from typing import Any, Dict, List

from langchain_community.utilities import ArxivAPIWrapper

from community.tools import BaseTool


class ArxivRetriever(BaseTool):
    NAME = "arxiv"

    def __init__(self):
        self.client = ArxivAPIWrapper()

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")
        result = self.client.run(query)
        return [{"text": result}]
