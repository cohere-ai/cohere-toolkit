from typing import Any, Dict, List

from langchain_community.document_loaders.weather import WeatherDataLoader

from community.tools import BaseRetrieval


class WeatherDataLoader(BaseRetrieval):
    def __init__(self):
        self.client = WeatherDataLoader()

    @classmethod
    def is_available(cls) -> bool:
        return True

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        result = self.client.from_params(query).load()
        return [{"text": result}]
