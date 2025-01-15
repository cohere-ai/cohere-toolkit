"""
Query and Path Parameters for Conversations
"""
from typing import Annotated

from fastapi import Path, Query

ConversationIdPathParam = Annotated[str, Path(
    title="Conversation ID",
    description="Conversation ID for conversation in question",
)]

QueryQueryParam = Annotated[str, Query(
    title="Query",
    description="Query string to search for in a conversation title",
)]
