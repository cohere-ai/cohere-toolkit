from pydantic import Field
from typing import List

from backend.schemas.chat import BaseChatRequest
from backend.schemas.tool import Tool


class LangchainChatRequest(BaseChatRequest):
    """
    Request shape for Langchain Streamed Chat.
    See: https://github.com/cohere-ai/cohere-python/blob/main/src/cohere/base_client.py#L1629
    """

    preamble: str | None = Field(
        default=None,
        title="A string to override the preamble.",
    )
    tools: List[Tool] = Field(
        default_factory=list,
        title="List of managed tools to use for the response.",
        exclude=True,
    )
