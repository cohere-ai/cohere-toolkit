from typing import Any, Dict, List

from langchain_community.tools.pubmed.tool import PubmedQueryRun

from community.tools import BaseTool


class PubMedRetriever(BaseTool):
    def __init__(self):
        self.client = PubmedQueryRun()

    @classmethod
    def is_available(cls) -> bool:
        return True

    def call(self, parameters: str, **kwargs: Any) -> List[Dict[str, Any]]:
        result = self.client.invoke(parameters)
        return [{"text": result}]
