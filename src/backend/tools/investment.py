import os
from typing import Any, Dict, List

from langchain_cohere import CohereEmbeddings, CohereRerank
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.pdf import PyMuPDFLoader

from dotenv import load_dotenv
load_dotenv()

from backend.chat.collate import RELEVANCE_THRESHOLD
from backend.tools.base import BaseTool


class MemoAnalyzer(BaseTool):
    """
    This class retrieves information and documents from the investment memos
    """

    NAME = "memo_analyzer"
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    FILEPATH = "src/backend/data/tfo/memo_index"
    USE_RERANK = True

    TOOL_DESCRIPTION = \
"""Retrieves information from memos to answer investment-related questions, for example in the case of a Private Equity investment, it would be the nature of investment ( e.g., acquisition, recapitalization, etc.,), the terms of the transaction (the value of the company, amount of equity invested, amount of leverage used, etc.), description of the underlying business and the industry, future financial projections, underwritten/projected returns on the investment, etc. """

    # search parameters
    TOP_K = 50
    TOP_N = 30

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
            docs.append(
                {
                    "title": doc.metadata.get("title", ""),
                    "text": doc.page_content,
                    "url": doc.metadata.get("source", ""),
                }
            )

        # rerank TOP_N documents
        if self.USE_RERANK:
            ranked_results = []
            results = self.rerank.rerank(
                query=query,
                documents=docs,
                rank_fields=["text", "source"],
                top_n=self.TOP_N,
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
    folder = "src/backend/data/tfo"
    urls = [
        "https://drive.google.com/file/d/1iequwjaDGzfScm79IWpKDLTr9IdFTuTr/view?usp=drive_link",
        "https://drive.google.com/file/d/1i2P9YL5R6-eHuJaWUpnbwYw6ITzrqfWf/view?usp=drive_link"
    ]
    files = ["investment-1.pdf", "investment-2.pdf"]
    for file, url in zip(files, urls):
        print(file)
        print(url)
        filepath = os.path.join(folder, file)
        loader = PyMuPDFLoader(filepath)
        _docs = loader.load()
        for doc in _docs:
            # remove "~" char to avoid strike through formatting in response
            doc.page_content = doc.page_content.replace("~", "")
            doc.metadata["source"] = url
            doc.metadata["title"] = file
        docs.extend(_docs)
        print(docs[0])

    db = FAISS.from_documents(
        docs,
        CohereEmbeddings(cohere_api_key=os.getenv("COHERE_API_KEY"), model="embed-english-v3.0")
    )

    db.save_local("src/backend/data/tfo/memo_index")