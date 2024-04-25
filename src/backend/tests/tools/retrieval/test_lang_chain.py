from unittest.mock import MagicMock, patch

from langchain_core.documents.base import Document

from backend.tools.retrieval.lang_chain import (
    LangChainVectorDBRetriever,
    LangChainWikiRetriever,
)


def test_wiki_retriever() -> None:
    retriever = LangChainWikiRetriever()
    query = "Python programming"
    mock_docs = [
        Document(
            page_content="example content",
            metadata={
                "title": "example title",
                "summary": "example summary",
                "source": "https://example.com",
            },
        ),
        Document(
            page_content="example content 2",
            metadata={
                "title": "example title 2",
                "summary": "example summary 2",
                "source": "https://example.com/2",
            },
        ),
    ]
    expected_docs = [
        {
            "text": "example content",
            "title": "example title",
            "url": "https://example.com",
        },
        {
            "text": "example content 2",
            "title": "example title 2",
            "url": "https://example.com/2",
        },
    ]

    wiki_retriever_mock = MagicMock()
    wiki_retriever_mock.get_relevant_documents.return_value = mock_docs

    with patch(
        "backend.tools.retrieval.lang_chain.WikipediaRetriever",
        return_value=wiki_retriever_mock,
    ):
        result = retriever.retrieve_documents(query)

    assert result == expected_docs


def test_wiki_retriever_no_docs() -> None:
    retriever = LangChainWikiRetriever()
    query = "Python programming"
    mock_docs = []

    wiki_retriever_mock = MagicMock()
    wiki_retriever_mock.get_relevant_documents.return_value = mock_docs

    with patch(
        "backend.tools.retrieval.lang_chain.WikipediaRetriever",
        return_value=wiki_retriever_mock,
    ):
        result = retriever.retrieve_documents(query)

    assert result == []


def test_vector_db_retriever() -> None:
    file_path = "src/backend/tests/test_data/Mariana_Trench.pdf"
    retriever = LangChainVectorDBRetriever(file_path)
    query = "What is the mariana trench?"
    mock_docs = [
        Document(
            page_content="Location of the Mariana TrenchMariana Trench",
            metadata={
                "page": 0,
                "source": "src/backend/tests/test_data/Mariana_Trench.pdf",
            },
        ),
        Document(
            page_content="Like other oceanic trenches, the Mariana Trench has been propos ed as a site for nuclear waste",
            metadata={
                "page": 4,
                "source": "src/backend/tests/test_data/Mariana_Trench.pdf",
            },
        ),
        Document(
            page_content="The Pacific plate is subducted beneath the Mariana Plate",
            metadata={
                "page": 1,
                "source": "src/backend/tests/test_data/Mariana_Trench.pdf",
            },
        ),
        Document(
            page_content='37. "Vityaz-D explored Mariana Trench according to preinstalled program — developer"',
            metadata={
                "page": 7,
                "source": "src/backend/tests/test_data/Mariana_Trench.pdf",
            },
        ),
    ]
    expected_docs = [
        {"text": "Location of the Mariana TrenchMariana Trench"},
        {
            "text": "Like other oceanic trenches, the Mariana Trench has been propos ed as a site for nuclear waste"
        },
        {"text": "The Pacific plate is subducted beneath the Mariana Plate"},
        {
            "text": '37. "Vityaz-D explored Mariana Trench according to preinstalled program — developer"'
        },
    ]

    db_get_relevant_docs_mock = MagicMock()
    db_get_relevant_docs_mock.get_relevant_docs.return_value = mock_docs

    with patch(
        "langchain_community.vectorstores.Chroma.from_documents"
    ) as mock_from_documents:
        mock_db = MagicMock()
        mock_from_documents.return_value = mock_db
        mock_db.as_retriever().get_relevant_documents.return_value = mock_docs
        result = retriever.retrieve_documents(query)

    assert result == expected_docs


def test_vector_db_retriever_no_docs() -> None:
    file_path = "src/backend/tests/test_data/Mariana_Trench.pdf"
    retriever = LangChainVectorDBRetriever(file_path)
    query = "What is the mariana trench?"
    mock_docs = []

    db_get_relevant_docs_mock = MagicMock()
    db_get_relevant_docs_mock.get_relevant_docs.return_value = mock_docs

    with patch(
        "langchain_community.vectorstores.Chroma.from_documents"
    ) as mock_from_documents:
        mock_db = MagicMock()
        mock_from_documents.return_value = mock_db
        mock_db.as_retriever().get_relevant_documents.return_value = mock_docs
        result = retriever.retrieve_documents(query)

    assert result == []
