from backend.chat.custom.model_deployments.cohere_platform import CohereDeployment
from backend.tools.retrieval import collate


def test_rerank() -> None:
    model = CohereDeployment()
    input = {
        "mountain": [{"text": "hill"}, {"text": "cable"}, {"text": "goat"}],
        "computer": [{"text": "software"}, {"text": "penguin"}, {"text": "cable"}],
    }
    assert collate.rerank(input, model) == {
        "mountain": [{"text": "hill"}, {"text": "goat"}, {"text": "cable"}],
        "computer": [{"text": "cable"}, {"text": "software"}, {"text": "penguin"}],
    }


def test_interleave() -> None:
    input = {
        "q1": [{"q1a": "a"}, {"q1b": "b"}, {"q1c": "c"}],
        "q2": [{"q2a": "a"}, {"q2b": "b"}, {"q2c": "c"}],
        "q3": [{"q3a": "a"}, {"q3b": "b"}, {"q3c": "c"}],
    }
    assert collate.interleave(input) == [
        {"q1a": "a"},
        {"q2a": "a"},
        {"q3a": "a"},
        {"q1b": "b"},
        {"q2b": "b"},
        {"q3b": "b"},
        {"q1c": "c"},
        {"q2c": "c"},
        {"q3c": "c"},
    ]
