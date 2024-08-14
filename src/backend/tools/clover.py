import os
from typing import Any, Dict, List

from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_cohere import CohereEmbeddings, CohereRerank
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv()

from backend.chat.collate import RELEVANCE_THRESHOLD
from backend.tools.base import BaseTool


class CloverDocumentRetriever(BaseTool):
    """
    This class retrieves documentation from the Clover doc portal about product
    information
    """

    NAME = "clover_retriver"
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    FILEPATH = "src/backend/data/clover/clover_index"
    USE_RERANK = True

    # search parameters
    TOP_K = 10
    TOP_N = 5

    # source
    STUB = "https://docs.clover.com/docs/"

    def __init__(self):
        # load cohere models
        self.embed = CohereEmbeddings(
            cohere_api_key=self.COHERE_API_KEY,
            model="embed-english-v3.0",
        )
        if self.USE_RERANK:
            self.rerank = CohereRerank(
                cohere_api_key=self.COHERE_API_KEY,
                model="rerank-english-v3.0"
            )

        # load vectorstore as retriever
        self.retriever = self._load_db().as_retriever(search_kwargs={"k": self.TOP_K})

    @classmethod
    def is_available(cls) -> bool:
        return cls.COHERE_API_KEY is not None and os.path.isdir(cls.FILEPATH)
    
    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")

        # retrieve documents
        _docs = self.retriever.invoke(query, input_type="search_query")
        # transform Document objs into dict w/ metadata for rerank
        docs = []
        for doc in _docs:
            # prep source for url
            url = doc.metadata.get("source", "").replace("src/backend/data/clover/", "")[:-5]
            docs.append(
                {
                    "text": doc.page_content,
                    "url": self.STUB + url,
                }
            )

        # rerank TOP_N documents
        if self.USE_RERANK:
            ranked_results = []
            results = self.rerank.rerank(
                query=query,
                documents=docs,
                rank_fields=["text", "source"],
                top_n=self.TOP_N
            )
            for res in results:
                idx = res['index']
                relevance_score = res['relevance_score']

                if relevance_score >= RELEVANCE_THRESHOLD:
                    doc = docs[idx]
                    ranked_results.append(
                        doc
                    )
            # return ranked results
            if len(ranked_results) < 1:
                return [{"text": "no information was found"}]
            return ranked_results
    
        # return non-ranked results
        if len(docs) < 1:
            return [{"text": "no information was found"}]
        return docs

    def _load_db(self) -> FAISS:
        try:
            db = FAISS.load_local(
                self.FILEPATH,
                self.embed,
                allow_dangerous_deserialization=True,
            )
        except:
            raise FileNotFoundError("No FAISS vectorstore found")
        return db


if __name__ == "__main__":

    docs = []
    folder = "src/backend/data/clover"

    for file in os.listdir(folder):
        if file.endswith(".html"):
            filepath = os.path.join(folder, file)
            loader = UnstructuredHTMLLoader(filepath)
            data = loader.load()
            docs.extend(data)

    db = FAISS.from_documents(
        docs,
        CohereEmbeddings(cohere_api_key=os.getenv("COHERE_API_KEY"), model="embed-english-v3.0")
    )

    db.save_local("src/backend/data/clover/clover_index")
