from typing import Any, Dict, List

from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.readers import StringIterableReader
from llama_index.embeddings.cohere import CohereEmbedding

import backend.crud.file as file_crud
from backend.config import Settings
from backend.schemas.context import Context
from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool

"""
Plug in your llama index retrieval implementation here.
We have an example flow with PDF upload.


More details:
https://docs.llamaindex.ai/en/stable/module_guides/querying/retriever/root.html
"""


class LlamaIndexUploadPDFRetriever(BaseTool):
    """
    This class retrieves documents from a PDF using the llama_index package.
    This requires llama_index package to be installed.
    """

    ID = "file_reader_llamaindex"
    CHUNK_SIZE = 512

    def __init__(self):
        self.COHERE_API_KEY = Settings().get('deployments.cohere_platform.api_key')


    def _get_embedding(self, embed_type):
        return CohereEmbedding(
            api_key=self.COHERE_API_KEY,
            model_name="embed-english-v3.0",
            input_type=embed_type,
        )

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,
            display_name="Llama File Reader",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query for retrieval.",
                    "type": "str",
                    "required": True,
                },
                "files": {
                    "description": "A list of files represented as tuples of (filename, file ID) to search over",
                    "type": "list[tuple[str, str]]",
                    "required": True,
                },

            },
            is_visible=False,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.FileLoader,
            description=(
                "Retrieves the most relevant documents from the uploaded "
                "files based on the query using Llama Index."
            )
        )

    async def call(
        self, parameters: dict, ctx: Context, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        query = parameters.get("query")
        files = parameters.get("files")
        session = kwargs.get("session")
        user_id = kwargs.get("user_id")

        if not query or not files:
            return []

        file_ids = [file_id for _, file_id in files]
        retrieved_files = file_crud.get_files_by_ids(session, file_ids, user_id)
        if not retrieved_files:
            return self.get_no_results_error()

        file_str_list = []
        for file in retrieved_files:
            file_str_list.append(file.file_content)
        # LLamaIndex get documents from parsed PDFs, split it into sentences, embed, index and retrieve
        try:
            docs = StringIterableReader().load_data(file_str_list)
            node_parser = SentenceSplitter(chunk_size=LlamaIndexUploadPDFRetriever.CHUNK_SIZE)
            nodes = node_parser.get_nodes_from_documents(docs)
            embed_model = self._get_embedding("search_document")
            vector_index = VectorStoreIndex(
                nodes,
                embed_model=embed_model,
            )
            embed_model_query = self._get_embedding("search_query")
            retriever = vector_index.as_retriever(
                similarity_top_k=10,
                embed_model=embed_model_query,
            )
            results = retriever.retrieve(query)
            llama_results = [{"text": doc.text} for doc in results]
        except Exception as e:
            return self.get_tool_error(details=str(e))

        if not llama_results and not docs:
            return self.get_no_results_error()

        # If llama results are found, return them
        if llama_results:
            return llama_results
        # If no llama results are found, return the original file content
        return [{"text": doc.text} for doc in docs]
