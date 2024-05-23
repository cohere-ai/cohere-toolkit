from typing import Any, Dict, List

from langchain_community.utilities import ArxivAPIWrapper

from community.tools import BaseTool


class ArxivRetriever(BaseTool):
    def __init__(self):
        self.client = ArxivAPIWrapper()

    @classmethod
    def is_available(cls) -> bool:
        return True

    def call(self, parameters: str, **kwargs: Any) -> List[Dict[str, Any]]:
        result = self.client.run(parameters)
        return [{"text": result}]
