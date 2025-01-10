"""
Query and Path Parameters for Conversations
"""
from typing import Annotated

from fastapi import Path

ConversationIdPathParam = Annotated[str, Path(
    title="Conversation ID",
    description="Conversation ID for conversation in question",
)]
