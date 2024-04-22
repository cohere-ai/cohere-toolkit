import os
from typing import Any, Dict, List

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import CohereEmbeddings
from langchain_community.retrievers import WikipediaRetriever
from langchain_community.vectorstores import Chroma

from backend.tools.retrieval.base import BaseRetrieval

"""
Plug in your lang chain retrieval implementation here. 
We have an example flows with wikipedia and vector DBs.

More details: https://python.langchain.com/docs/integrations/retrievers
"""


class LangChainWikiRetriever(BaseRetrieval):
    """
    This class retrieves documents from Wikipedia using the langchain package.
    This requires wikipedia package to be installed:
    pip install wikipedia-api
    """

    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 0):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        wiki_retriever = WikipediaRetriever()
        docs = wiki_retriever.get_relevant_documents(query)
        text_splitter = CharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        documents = text_splitter.split_documents(docs)
        return [
            {
                "text": doc.page_content,
                "title": doc.metadata.get("title", None),
                "url": doc.metadata.get("source", None),
            }
            for doc in documents
        ]


class LangChainVectorDBRetriever(BaseRetrieval):
    """
    This class retrieves documents from a vector database using the langchain package.
    This requires chromadb package to be installed:
     pip install chromadb
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        cohere_embeddings = CohereEmbeddings(
            cohere_api_key=os.environ["COHERE_API_KEY"]
        )
        # Load text files and split into chunks
        loader = PyPDFLoader(self.filepath)
        text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        pages = loader.load_and_split(text_splitter)
        # Create a vector store from the documents
        db = Chroma.from_documents(pages, cohere_embeddings)
        input_docs = db.as_retriever().get_relevant_documents(query)
        return [dict({"text": doc.page_content}) for doc in input_docs]
