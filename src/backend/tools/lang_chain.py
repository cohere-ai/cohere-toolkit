from typing import Any

from langchain.text_splitter import CharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.retrievers import WikipediaRetriever
from langchain_community.vectorstores import Chroma

from backend.config.settings import Settings
from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
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
    ID = "wikipedia"

    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 0):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Wikipedia",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query for retrieval.",
                    "type": "str",
                    "required": True,
                }
            },
            kwargs={"chunk_size": 300, "chunk_overlap": 0},
            is_visible=True,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.DataLoader,
            description="Retrieves documents from Wikipedia.",
        ) # type: ignore

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any,
    ) -> list[dict[str, Any]]:
        wiki_retriever = WikipediaRetriever()
        query = parameters.get("query", "")
        try:
            docs = wiki_retriever.get_relevant_documents(query)
            text_splitter = CharacterTextSplitter(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
            documents = text_splitter.split_documents(docs)
        except Exception as e:
            return self.get_tool_error(details=str(e))

        if not documents:
            return self.get_no_results_error()

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
    ID = "vector_retriever"
    COHERE_API_KEY = Settings().get('deployments.cohere_platform.api_key')

    def __init__(self, filepath: str):
        self.filepath = filepath

    @classmethod
    def is_available(cls) -> bool:
        return cls.COHERE_API_KEY is not None

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Vector DB Retriever",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query for retrieval.",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=False,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.DataLoader,
            description="Retrieves documents from Wikipedia.",
        ) # type: ignore

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any,
    ) -> list[dict[str, Any]]:
        cohere_embeddings = CohereEmbeddings(cohere_api_key=self.COHERE_API_KEY)

        # Load text files and split into chunks
        try:
            loader = PyPDFLoader(self.filepath)
            text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
            pages = loader.load_and_split(text_splitter)

            # Create a vector store from the documents
            db = Chroma.from_documents(documents=pages, embedding=cohere_embeddings)
            query = parameters.get("query", "")
            input_docs = db.as_retriever().get_relevant_documents(query)
        except Exception as e:
            return self.get_tool_error(details=str(e))
        if not input_docs:
            return self.get_no_results_error()

        return [{"text": doc.page_content} for doc in input_docs]
