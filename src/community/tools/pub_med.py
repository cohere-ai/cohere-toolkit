from typing import Any, Dict, List

from langchain_community.tools.pubmed.tool import PubmedQueryRun

from community.tools import BaseTool


class PubMedRetriever(BaseTool):
    NAME = "pub_med"

    def __init__(self):
        self.client = PubmedQueryRun()

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")
        result = self.client.invoke(query)
        return [{"text": result}]
