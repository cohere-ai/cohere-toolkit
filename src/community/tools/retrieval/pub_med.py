from typing import Any, Dict, List

from langchain_community.tools.pubmed.tool import PubmedQueryRun

from community.tools import BaseRetrieval


class PubMedRetriever(BaseRetrieval):
    def __init__(self):
        self.client = PubmedQueryRun()

    @classmethod
    def is_available(cls) -> bool:
        return True

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        result = self.client.invoke(query)
        return [{"text": result}]
