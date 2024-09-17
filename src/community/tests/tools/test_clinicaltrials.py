import pytest

from community.tools import ClinicalTrials


@pytest.mark.asyncio
async def test_clinicaltrials_tool():
    retriever = ClinicalTrials()
    result = await retriever.call(
        parameters={
            "condition": "lung cancer",
            "location": "Canada",
            "is_recruiting": True,
        }
    )
    assert len(result) > 0
    assert "id" in result[0]
