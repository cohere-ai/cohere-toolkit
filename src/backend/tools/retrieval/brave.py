# https://python.langchain.com/docs/integrations/tools/brave_search/

import json
import os
from typing import Any, Dict, List

import dotenv
from langchain_community.tools import BraveSearch

from backend.tools.retrieval.base import BaseRetrieval


class BraveSearchRetriever(BaseRetrieval):
    def __init__(self, count: int = 3):
        if "BRAVE_SEARCH_API_KEY" not in os.environ:
            raise ValueError(
                "Please set the BRAVE_SEARCH_API_KEY environment variable."
            )

        self.api_key = os.environ["BRAVE_SEARCH_API_KEY"]
        self.tool = BraveSearch.from_api_key(
            api_key=self.api_key, search_kwargs={"count": count}
        )

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        results_string = self.tool.run(query)
        results = json.loads(results_string)
        return [
            {
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "text": result.get("snippet", ""),
            }
            for result in results
        ]


if __name__ == "__main__":
    dotenv.load_dotenv()
    retriever = BraveSearchRetriever()
    retriever.retrieve_documents("python")
