import pytest

from community.tools import PubMedRetriever


@pytest.mark.asyncio
async def test_pub_med_retriever():
    retriever = PubMedRetriever()
    result = await retriever.call({"query": "What causes lung cancer?"})
    assert len(result) > 0
    assert "text" in result[0]
