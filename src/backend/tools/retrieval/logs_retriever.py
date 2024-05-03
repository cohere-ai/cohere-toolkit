from typing import Any, List, Dict
from elasticsearch import Elasticsearch
from backend.tools.retrieval.base import BaseRetrieval
import os
from backend.services.logger import get_logger

cohere_api_key = os.environ.get("COHERE_API_KEY")
logger = get_logger()


class LogsRetriever(BaseRetrieval):
    def __init__(
            self,
            host_url: str,
            index: str,
            deployment_name: str,
    ) -> None:
        self.index = index
        self.deployment_name = deployment_name
        self.client = Elasticsearch(host_url)
        self.cohere_api_key = os.environ.get("COHERE_API_KEY")

    @classmethod
    def is_available(cls) -> bool:
        return cohere_api_key is not None

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        query_dict = {
            "query": {
                "match": {"message": query}
            }
        }
        res = self.client.search(index=self.index, body=query_dict)

        logger.info(f"Retrieving response {res}")

        docs = []
        for r in res["hits"]["hits"]:
            docs.append({
                "text": r["_source"]["message"],
                "url": r["_source"]["url"],
            })

        return docs
