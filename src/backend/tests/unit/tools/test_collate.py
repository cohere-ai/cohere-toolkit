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
async def test_rerank() -> None:
    model = CohereDeployment(model_config={})
    outputs = [
        {
            "text": "Mount Everest is Earth's highest mountain above sea level, located in the Mahalangur Himal sub-range of the Himalayas"
        },
        {
            "text": "There are four components - or parts - of the blood: red blood cells, white blood cells, plasma and platelets."
        },
        {
            "text": "'My Man Rocks Me (with One Steady Roll)' by Trixie Smith was issued in 1922, the first record to refer to 'rocking' and 'rolling' in a secular context"
        },
    ]
    tool_results = [
        {
            "call": {
                "parameters": {"query": "what is the highest mountain in the world?"},
                "name": "retriever",
            },
            "outputs": outputs,
        },
        {
            "call": {
                "parameters": {"query": "What are the 4 major components of blood?"},
                "name": "retriever",
            },
            "outputs": outputs,
        },
        {
            "call": {
                "parameters": {"query": "When was 1st Olympics in history?"},
                "name": "retriever",
            },
            "outputs": outputs,
        },
    ]

    expected_output = [
        {
            "call": {
                "parameters": {"query": "what is the highest mountain in the world?"},
                "name": "retriever",
            },
            "outputs": [outputs[0], outputs[1], outputs[2]],
        },
        {
            "call": {
                "parameters": {"query": "What are the 4 major components of blood?"},
                "name": "retriever",
            },
            "outputs": [outputs[1]],
        },
        {
            "call": {
                "parameters": {"query": "When was 1st Olympics in history?"},
                "name": "retriever",
            },
            "outputs": [],
        },
    ]

    assert await collate.rerank_and_chunk(tool_results, model) == expected_output


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
