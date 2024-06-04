from typing import Any, Dict, List

from pypdf import PdfReader

import backend.crud.file as file_crud
from backend.chat.collate import combine_documents
from backend.tools.base import BaseTool


class ReadFileTool(BaseTool):
    """
    This class reads a file from the file system.
    """

    MAX_NUM_CHUNKS = 10

    def __init__(self):
        pass

    @classmethod
    def is_available(cls) -> bool:
        return True

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        file_name = parameters.get("filename", "")
        session = kwargs.get("session")
        user_id = kwargs.get("user_id")

        if not file_name:
            return []

        files = file_crud.get_files_by_file_names(session, [file_name], user_id)

        if not files:
            return []

        file = files[0]
        chunks = chunk_document(file.file_content)
        result = [
            {
                "text": chunk,
                "title": file.file_name,
                "url": file.file_path,
            }
            for chunk in chunks
        ]

        return result


class SearchFileTool(BaseTool):
    """
    This class searches for a query in a file.
    """

    MAX_NUM_CHUNKS = 10

    def __init__(self):
        pass

    @classmethod
    def is_available(cls) -> bool:
        return True

    def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        query = parameters.get("search_query")
        file_names = parameters.get("filenames")
        model_deployment = kwargs.get("model_deployment")
        session = kwargs.get("session")
        user_id = kwargs.get("user_id")

        if not query or not file_names:
            return []

        files = file_crud.get_files_by_file_names(session, file_names, user_id)

        if not files:
            return []

        files_dicts = []
        for file in files:
            chunks = chunk_document(file.file_content)
            for chunk in chunks:
                files_dicts.append(
                    {
                        "text": chunk,
                        "title": file.file_name,
                        "url": file.file_path,
                    }
                )

        # Combine and rerank the documents
        result = combine_documents({query: files_dicts}, model_deployment)

        # return top results
        num_chunks = min(len(result), self.MAX_NUM_CHUNKS)
        return result[:num_chunks]


def get_file_content(file_path):
    # Currently only supports PDF files
    loader = PdfReader(file_path)
    text = ""
    for page in loader.pages:
        text += page.extract_text() + "\n"

    return text


def chunk_document(
    content, compact_mode=False, soft_word_cut_off=100, hard_word_cut_off=300
):
    if compact_mode:
        content = content.replace("\n", " ")

    chunks = []
    current_chunk = ""
    words = content.split()
    word_count = 0

    for word in words:
        if word_count + len(word.split()) > hard_word_cut_off:
            # If adding the next word exceeds the hard limit, finalize the current chunk
            chunks.append(current_chunk)
            current_chunk = ""
            word_count = 0

        if word_count + len(word.split()) > soft_word_cut_off and word.endswith("."):
            # If adding the next word exceeds the soft limit and the word ends with a period, finalize the current chunk
            current_chunk += " " + word
            chunks.append(current_chunk.strip())
            current_chunk = ""
            word_count = 0
        else:
            # Add the word to the current chunk
            if current_chunk == "":
                current_chunk = word
            else:
                current_chunk += " " + word
            word_count += len(word.split())

    # Add any remaining content as the last chunk
    if current_chunk != "":
        chunks.append(current_chunk.strip())

    return chunks
