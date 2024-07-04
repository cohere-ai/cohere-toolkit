import os
from typing import Any, Dict, List

from langchain.vectorstores.faiss import FAISS
from langchain_cohere import CohereEmbeddings, CohereRerank
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from src.backend.chat.collate import RELEVANCE_THRESHOLD

from dotenv import load_dotenv
load_dotenv()

from backend.tools.base import BaseTool
    

class YelpReranker(BaseTool):
    """
    Retrieves user reviews about businesses from a yelp dataset and ranks them
    based on query sentiment.
    """
    cohere_api_key = os.environ.get("COHERE_API_KEY")
    filepath = "/workspace/src/backend/data/yelp/review_index"

    def __init__(self):

        self.filepath = "/workspace/src/backend/data/yelp/review_index"
        self.cohere_api_key = os.environ.get("COHERE_API_KEY")
        
        # load cohere models
        self.embed = CohereEmbeddings(
            cohere_api_key=self.cohere_api_key,
            model="embed-english-v3.0",
        )

        self.rerank_model = CohereRerank(
            cohere_api_key=self.cohere_api_key,
            model="rerank-english-v3.0"
        )

        # load vectorstore as retriever
        self.retriever = self._load_db()

    def _load_db(self) -> FAISS:
        try:
            db = FAISS.load_local(
                self.filepath,
                self.embed,
                allow_dangerous_deserialization=True
            )
        except:
            raise FileNotFoundError("No vectorstore found")
        return db

    @classmethod
    def is_available(cls) -> bool:
        return cls.cohere_api_key is not None and os.path.isdir(cls.filepath)
    
    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")
        top_k = parameters.get("top_k", 3)

        self.rerank = ContextualCompressionRetriever(
            base_compressor=self.rerank_model,
            base_retriever=self.retriever.as_retriever(search_kwargs={"k": top_k})
        )

        results = self.rerank.invoke(query)
        for res in results:
            print(res)
            print("\n\n")

        results = [
            {
                "name": doc.metadata["name"],
                "text": doc.page_content
            } for doc in results if doc.metadata["relevance_score"] >= RELEVANCE_THRESHOLD
        ]

        if len(results) == 0:
            print("XXXXXXXXXXXXXX HIT")
            return [{"text": "nothing was found"}]
        
        return results
