import os
from typing import Any, Dict, List

from elasticsearch import Elasticsearch

from backend.services.logger import get_logger
from backend.tools.retrieval.base import BaseRetrieval

cohere_api_key = os.environ.get("COHERE_API_KEY")
logger = get_logger()


class ElasticSearchRetriever(BaseRetrieval):
    index = os.getenv("ELASTICSEARCH_INDEX", None)
    host = os.getenv("ELASTICSEARCH_HOST", None)

    def __init__(
        self,
        deployment_name: str,
    ) -> None:
        self.deployment_name = deployment_name
        self.client = Elasticsearch(self.host)

    @classmethod
    def is_available(cls) -> bool:
        return all([cls.index is not None, cls.host is not None])

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        query_dict = {"query": {"match": {"message": query}}}
        res = self.client.search(index=self.index, body=query_dict)

        logger.info(f"Retrieving response {res}")

        docs = []
        for r in res["hits"]["hits"]:
            docs.append(
                {
                    "text": r["_source"]["message"],
                    "url": r["_source"]["url"],
                }
            )

        return docs
