from typing import Any, Dict, List

from llama_index.core import SimpleDirectoryReader

from community.tools import BaseTool

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

    NAME = "file_reader_llamaindex"

    def __init__(self, filepath: str):
        self.filepath = filepath

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        docs = SimpleDirectoryReader(input_files=[self.filepath]).load_data()
        return [dict({"text": doc.text}) for doc in docs]
