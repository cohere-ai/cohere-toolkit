from community.tools.function_tools.clinicaltrials import ClinicalTrialsTool


def test_clinicaltrials_tool():
    retriever = ClinicalTrialsTool()
    result = retriever.call(
        parameters={
            "condition": "lung cancer",
            "location": "Canada",
            "is_recruiting": True,
        }
    )
    assert len(result) > 0
    assert "id" in result[0]
