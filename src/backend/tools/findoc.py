import os
import pickle
import uuid
import cohere
from typing import Any, Dict, List
from langchain_cohere import CohereEmbeddings
from langchain_core.documents import Document
from langchain_core.stores import InMemoryStore
from langchain_chroma import Chroma
from langchain.retrievers import MultiVectorRetriever

from backend.tools.base import BaseTool

from dotenv import load_dotenv
load_dotenv()


class FinanceParser(BaseTool):
    """
    This class reads a financial document from the file system.
    """

    NAME = "fin_parser"
    COHERE_API_KEY = os.getenv("COHERE_API_KEY") 
    EMBED_MODEL = "embed-english-v3.0"
    RERANK_MODEL = "rerank-english-v3.0"
    CHAT_MODEL = "command-r-plus"
    FILEPATH = "src/backend/data/bdc"
    TOP_N = 3
    
    def __init__(self):
        # Generate table and text summaries
        prompt_text = \
        """
        ## Purpose
        You are an assistant tasked with summarizing tables and text.

        ## Task
        Give a concise summary of the content in the table or text Only provide the summary and no other text.

        ## Content in Table or Text
        {element}
        """

        self.co = cohere.Client(api_key=self.COHERE_API_KEY)

        # Load element lists
        with open("src/backend/data/bdc/tables.pkl", "rb") as f:
            table_elements = pickle.load(f)
        with open("src/backend/data/bdc/texts.pkl", "rb") as f:
            text_elements = pickle.load(f)
        
        self.retriever = self._generate_vectorstore(prompt_text, table_elements, text_elements)

    @classmethod
    def is_available(cls) -> bool:
        return cls.COHERE_API_KEY is not None and os.path.isdir(cls.FILEPATH)

    async def call(
        self, parameters: dict, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")

        search_query = self.co.chat(message=query, model=self.CHAT_MODEL, temperature=0.2, search_queries_only=True)

        reranked_docs = []
        for sq in search_query.search_queries:
            docs = self.retriever.invoke(sq.text)
            _reranked_docs = self._rerank(sq.text, docs)
            reranked_docs.extend(_reranked_docs)

        documents = [
            {
                "title": f"Apple-10k.pdf (Chunk {i})",
                "text": reranked_docs[i],
                "url": "https://d18rn0p25nwr6d.cloudfront.net/CIK-0000320193/ee662306-a551-4192-91d8-e9931452076e.pdf"
            }
            for i in range(len(reranked_docs))
        ]

        if len(documents) > 0:
            return documents
        else:
            return [{"text": "No relevant documents found."}]

    
    def _generate_vectorstore(self, prompt_text: str, tables: list, texts: list) -> MultiVectorRetriever:
        # load table and text summaries
        with open("/src/backend/data/bdc/table_summaries.pkl", "rb") as f:
            table_summaries = pickle.load(f)
        with open("/src/backend/data/bdc/text_summaries.pkl", "rb") as f:
            text_summaries = pickle.load(f)

        tables = [element.text for element in tables]
        texts = [element.text for element in texts]

        # Setup vectorstore
        vectorstore = Chroma(
            collection_name="summaries", 
            embedding_function=CohereEmbeddings(cohere_api_key=self.COHERE_API_KEY, model=self.EMBED_MODEL)
        )
        store = InMemoryStore()
        id_key = "doc_id"

        retriever = MultiVectorRetriever(
            vectorstore=vectorstore,
            docstore=store,
            id_key=id_key
        )

        # Store tables
        table_ids = [str(uuid.uuid4()) for _ in tables]
        docs_tables = [
            Document(page_content=s, metadata={id_key: table_ids[i]})
            for i, s in enumerate(table_summaries)
        ]
        retriever.vectorstore.add_documents(docs_tables)
        retriever.docstore.mset(list(zip(table_ids, tables)))

        # Store texts
        doc_ids = [str(uuid.uuid4()) for _ in texts]
        docs_texts = [
            Document(page_content=s, metadata={id_key: doc_ids[i]})
            for i, s in enumerate(text_summaries)
        ]
        retriever.vectorstore.add_documents(docs_texts)
        retriever.docstore.mset(list(zip(doc_ids, texts)))

        return retriever
    
    def _rerank(self, query: str, documents: list) -> list[str]:
        response = self.co.rerank(
            query=query,
            documents=documents,
            top_n=self.TOP_N,
            model=self.RERANK_MODEL,
            return_documents=True
        )
        top_chunks_after_reranking = [result.document.text for result in response.results]
        return top_chunks_after_reranking
