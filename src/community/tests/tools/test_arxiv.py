import pytest

from community.tools import ArxivRetriever


@pytest.mark.asyncio
async def test_arxiv_retriever():
    retriever = ArxivRetriever()
    result = await retriever.call({"query": "quantum"})
    assert len(result) > 0
    assert "text" in result[0]
    assert "quantum" in result[0]["text"].lower()
