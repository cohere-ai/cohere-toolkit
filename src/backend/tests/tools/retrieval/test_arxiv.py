from backend.tools.retrieval.arxiv import ArxivRetriever


def test_arxiv_retriever():
    retriever = ArxivRetriever()
    result = retriever.retrieve_documents("quantum")
    assert len(result) > 0
    assert "text" in result[0]
    assert "quantum" in result[0]["text"].lower()
