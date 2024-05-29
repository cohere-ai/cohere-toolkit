import os

import pytest

from backend.chat import collate
from backend.model_deployments import CohereDeployment

is_cohere_env_set = (
    os.environ.get("COHERE_API_KEY") is not None
    and os.environ.get("COHERE_API_KEY") != ""
)


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_rerank() -> None:
    model = CohereDeployment(model_config={})
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
