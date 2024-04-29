from typing import Any, Dict, List

from langchain_community.utilities import ArxivAPIWrapper

from backend.tools.retrieval.base import BaseRetrieval


class ArxivRetriever(BaseRetrieval):
    def __init__(self):
        self.client = ArxivAPIWrapper()

    @classmethod
    def is_available(cls) -> bool:
        return True

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        result = self.client.run(query)
        return [{"text": result}]
