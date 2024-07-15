from enum import StrEnum
from typing import Any, Dict, List

from pydantic import Field

from backend.schemas.chat import BaseChatRequest


class CohereChatPromptTruncation(StrEnum):
    """Dictates how the prompt will be constructed. Defaults to "AUTO_PRESERVE_ORDER"."""

    OFF = "OFF"
    AUTO_PRESERVE_ORDER = "AUTO_PRESERVE_ORDER"


class CohereChatRequest(BaseChatRequest):
    """
    Request shape for Cohere Python SDK Streamed Chat.
    See: https://github.com/cohere-ai/cohere-python/blob/main/src/cohere/base_client.py#L1629
    """

    documents: List[Dict[str, Any]] = Field(
        default_factory=list,
        title="""Documents to use to generate grounded response with citations. Example:
            documents=[
                {
                    "id": "national_geographic_everest",
                    "title": "Height of Mount Everest",
                    "text": "The height of Mount Everest is 29,035 feet",
                    "url": "https://education.nationalgeographic.org/resource/mount-everest/",
                },
                {
                    "id": "national_geographic_mariana",
                    "title": "Depth of the Mariana Trench",
                    "text": "The depth of the Mariana Trench is 36,070 feet",
                    "url": "https://www.nationalgeographic.org/activity/mariana-trench-deepest-place-earth",
                },
            ]
        """,
    )
    model: str | None = Field(
        default="command-r",
        title="The model to use for generating the response.",
    )
    temperature: float | None = Field(
        default=None,
        title="A non-negative float that tunes the degree of randomness in generation. Lower temperatures mean less random generations, and higher temperatures mean more random generations.",
        ge=0,
    )
    k: int | None = Field(
        default=None,
        title="Ensures only the top k most likely tokens are considered for generation at each step.",
        le=500,
        ge=0,
    )
    p: float | None = Field(
        default=None,
        title="Ensures that only the most likely tokens, with total probability mass of p, are considered for generation at each step. If both k and p are enabled, p acts after k.",
        le=0.99,
        ge=0,
    )
    preamble: str | None = Field(
        default=None,
        title="A string to override the preamble.",
    )
    file_ids: List[str] | None = Field(
        default=None,
        title="List of File IDs for PDFs used in RAG for the response.",
        exclude=True,
    )
    search_queries_only: bool | None = Field(
        default=False,
        title="When set to true a list of search queries are generated. No search will occur nor replies to the user's message.",
    )
    max_tokens: int | None = Field(
        default=None,
        title="The maximum number of tokens the model will generate as part of the response. Note: Setting a low value may result in incomplete generations.",
        ge=1,
    )
    seed: float | None = Field(
        default=None,
        title="If specified, the backend will make a best effort to sample tokens deterministically, such that repeated requests with the same seed and parameters should return the same result. However, determinism cannot be totally guaranteed.",
    )
    stop_sequences: List[str] | None = Field(
        default=None,
        title="A list of up to 5 strings that the model will use to stop generation. If the model generates a string that matches any of the strings in the list, it will stop generating tokens and return the generated text up to that point not including the stop sequence.",
    )
    presence_penalty: float | None = Field(
        default=None,
        title="Used to reduce repetitiveness of generated tokens. Similar to frequency_penalty, except that this penalty is applied equally to all tokens that have already appeared, regardless of their exact frequencies.",
        ge=0,
        le=1,
    )
    frequency_penalty: float | None = Field(
        default=None,
        title="Used to reduce repetitiveness of generated tokens. The higher the value, the stronger a penalty is applied to previously present tokens, proportional to how many times they have already appeared in the prompt or prior generation.",
        ge=0,
        le=1,
    )
    prompt_truncation: CohereChatPromptTruncation = Field(
        default=CohereChatPromptTruncation.AUTO_PRESERVE_ORDER,
        title="Dictates how the prompt will be constructed. Defaults to 'AUTO_PRESERVE_ORDER'.",
    )
    tool_results: List[Dict[str, Any]] | None = Field(
        default=None,
        title="A list of results from invoking tools recommended by the model in the previous chat turn. Results are used to produce a text response and will be referenced in citations.",
    )
    force_single_step: bool | None = Field(
        default=None,
        title="If set to true, the model will generate a single response in a single step. This is useful for generating a response to a single message.",
    )
    agent_id: str | None = Field(
        default=None,
        title="The agent ID to use for the chat.",
    )
