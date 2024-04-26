from typing import Any, Dict, List

from langchain_community.tools.pubmed.tool import PubmedQueryRun

from community.tools import BaseRetrieval


class PubMedRetriever(BaseRetrieval):
    def __init__(self):
        self.tool = PubmedQueryRun()

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        result = self.tool.invoke(query)
        return [{"text": result}]
