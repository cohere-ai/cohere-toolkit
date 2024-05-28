from community.tools import PubMedRetriever


def test_pub_med_retriever():
    retriever = PubMedRetriever()
    result = retriever.call({"query": "What causes lung cancer?"})
    assert len(result) > 0
    assert "text" in result[0]
