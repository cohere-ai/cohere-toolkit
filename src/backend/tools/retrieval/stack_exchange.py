# https://python.langchain.com/docs/integrations/tools/stackexchange/

from typing import Any, Dict, List

from langchain_community.utilities import StackExchangeAPIWrapper

from backend.tools.retrieval.base import BaseRetrieval


class StackExchangeRetriever(BaseRetrieval):
    def __init__(self):
        self.tool = StackExchangeAPIWrapper()

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        result = self.tool.run(query)
        return [{"text": result}]


if __name__ == "__main__":
    retriever = StackExchangeRetriever()
    retriever.retrieve_documents("python")
