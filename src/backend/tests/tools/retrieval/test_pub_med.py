from backend.tools.retrieval.pub_med import PubMedRetriever


def test_pub_med_retriever():
    retriever = PubMedRetriever()
    result = retriever.retrieve_documents("What causes lung cancer?")
    assert len(result) > 0
    assert "text" in result[0]
