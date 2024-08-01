from typing import Any, Dict, List

from langchain.text_splitter import CharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.retrievers import WikipediaRetriever
from langchain_community.vectorstores import Chroma

from backend.config.settings import Settings
from backend.model_deployments.cohere_platform import COHERE_API_KEY_ENV_VAR
from backend.tools.base import BaseTool

"""
Plug in your lang chain retrieval implementation here. 
We have an example flows with wikipedia and vector DBs.

More details: https://python.langchain.com/docs/integrations/retrievers
"""


class LangChainWikiRetriever(BaseTool):
    """
    This class retrieves documents from Wikipedia using the langchain package.
    This requires wikipedia package to be installed.
    """

    NAME = "wikipedia"

    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 0):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        wiki_retriever = WikipediaRetriever()
        query = parameters.get("query", "")
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


class LangChainVectorDBRetriever(BaseTool):
    """
    This class retrieves documents from a vector database using the langchain package.
    """

    NAME = "vector_retriever"
    COHERE_API_KEY = Settings().deployments.cohere_platform.api_key

    def __init__(self, filepath: str):
        self.filepath = filepath

    @classmethod
    def is_available(cls) -> bool:
        return cls.COHERE_API_KEY is not None

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        cohere_embeddings = CohereEmbeddings(cohere_api_key=self.COHERE_API_KEY)

        # Load text files and split into chunks
        loader = PyPDFLoader(self.filepath)
        text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        pages = loader.load_and_split(text_splitter)

        # Create a vector store from the documents
        db = Chroma.from_documents(documents=pages, embedding=cohere_embeddings)
        query = parameters.get("query", "")
        input_docs = db.as_retriever().get_relevant_documents(query)

        return [dict({"text": doc.page_content}) for doc in input_docs]
