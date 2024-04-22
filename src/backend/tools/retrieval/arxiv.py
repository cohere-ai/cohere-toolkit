from backend.tools.retrieval import BaseRetrieval
from langchain_community.utilities import ArxivAPIWrapper
from typing import Any, Dict, List


class ArxivRetriever(BaseRetrieval):
    def __init__(self):
        self.tool = ArxivAPIWrapper()

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        result = self.tool.run(query)
        return [{"text": result}]
