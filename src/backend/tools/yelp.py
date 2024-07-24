import os
from typing import Any, Dict, List

from langchain.vectorstores.faiss import FAISS
from langchain_cohere import CohereEmbeddings, CohereRerank
from backend.chat.collate import RELEVANCE_THRESHOLD

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

        self.rerank = CohereRerank(
            cohere_api_key=self.cohere_api_key,
            model="rerank-english-v3.0"
        )

        # load vectorstore as retriever
        self.retriever = self._load_db().as_retriever(search_kwargs={"k": 100})

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
        top_n = int(parameters.get("top_n", 3))
        ranked_results = []

        # self.rerank = ContextualCompressionRetriever(
        #     base_compressor=self.rerank_model,
        #     base_retriever=self.retriever.as_retriever(search_kwargs={"k": 100})
        # )

        # results = self.rerank.invoke(query)

        _docs = self.retriever.invoke(query, input_type="search_query")

        # transform Document objs into dict w/ metadata for rerank
        # TODO: make more efficient
        docs = []

        for doc in _docs:
            docs.append(
                {
                    "text": doc.page_content,
                    "name": doc.metadata.get("name", ""),
                    "date": doc.metadata.get("date", "").strftime("%Y-%m-%d %H:%M:%S"),
                    "city": doc.metadata.get("city", ""),
                    "state": doc.metadata.get("state", ""),
                    "review_rating": doc.metadata.get("user_stars", ""),
                    "avg_rating": doc.metadata.get("stars", ""),
                    "review_count": doc.metadata.get("review_count", ""),
                    "tags": doc.metadata.get("tags", "")
                }
            )

        results = self.rerank.rerank(
            query=query,
            documents=docs,
            rank_fields=["text", "name", "date"],
            top_n=top_n
        )

        for res in results:

            idx = res['index']
            relevance_score = res['relevance_score']
            print(idx, relevance_score)

            if relevance_score >= RELEVANCE_THRESHOLD:
                doc = docs[idx]

                print(doc)

                ranked_results.append(
                    doc
                )
    
        # ranked_results = [
        #     {
        #         "name": doc.metadata["name"],
        #         "text": doc.page_content
        #     } for doc in results if doc.metadata["relevance_score"] >= RELEVANCE_THRESHOLD
        # ]

        if len(ranked_results) == 0:
            print("XXX NO DOCUMENTS HIT")
            return [{"text": "nothing was found"}]
        
        return ranked_results
