import os

import pytest

from backend.chat import collate
from backend.model_deployments import CohereDeployment
from backend.schemas.tool import ToolCall

is_cohere_env_set = (
    os.environ.get("COHERE_API_KEY") is not None
    and os.environ.get("COHERE_API_KEY") != ""
)


@pytest.mark.skipif(not is_cohere_env_set, reason="Cohere API key not set")
def test_rerank() -> None:
    model = CohereDeployment(model_config={})
    tool_results = [
        {
            "call": ToolCall(parameters={"query": "mountain"}, name="retriever"),
            "outputs": [{"text": "hill"}, {"text": "goat"}, {"text": "cable"}],
        },
        {
            "call": ToolCall(parameters={"query": "computer"}, name="retriever"),
            "outputs": [{"text": "cable"}, {"text": "software"}, {"text": "penguin"}],
        },
    ]

    expected_output = [
        {
            "call": ToolCall(name="retriever", parameters={"query": "mountain"}),
            "outputs": [],
        },
        {
            "call": ToolCall(name="retriever", parameters={"query": "computer"}),
            "outputs": [],
        },
    ]

    assert collate.rerank_and_chunk(tool_results, model) == expected_output


def test_chunk_normal_mode() -> None:
    content = "This is a test. We are testing the chunk function."
    expected_output = ["This is a test.", "We are testing the chunk function."]
    collate.chunk(content, False, 4, 10) == expected_output


def test_chunk_compact_mode() -> None:
    content = "This is a test.\nWe are testing the chunk function."
    expected_output = ["This is a test.", "We are testing the chunk function."]
    collate.chunk(content, True, 4, 10) == expected_output


def test_chunk_hard_cut_off() -> None:
    content = "This is a test. We are testing the chunk function. This sentence will exceed the hard cut off."
    expected_output = [
        "This is a test. We are testing the chunk function.",
        "This sentence will exceed the hard cut off.",
    ]
    collate.chunk(content, False, 4, 10) == expected_output


def test_chunk_soft_cut_off() -> None:
    content = "This is a test. We are testing the chunk function. This sentence will exceed the soft cut off."
    expected_output = [
        "This is a test.",
        "We are testing the chunk function. This sentence will exceed the soft cut off.",
    ]
    collate.chunk(content, False, 4, 10) == expected_output


def test_chunk_empty_content() -> None:
    content = ""
    expected_output = []
    collate.chunk(content, False, 4, 10) == expected_output
