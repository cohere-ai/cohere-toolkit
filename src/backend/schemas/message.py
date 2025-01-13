import datetime
from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field

from backend.database_models.message import MessageAgent
from backend.schemas.citation import Citation
from backend.schemas.document import Document
from backend.schemas.file import ConversationFilePublic
from backend.schemas.tool import ToolCall


class MessageBase(ABC, BaseModel):
    """
    Abstract class for Message schemas
    """
    text: str = Field(
        ...,
        title="Text",
        description="The text content of the message",
    )


class Message(MessageBase):
    """
    Message Schema
    """
    id: str = Field(
        ...,
        title="ID",
        description="Unique identifier of the message",
    )
    created_at: datetime.datetime = Field(
        ...,
        title="Created At Timestamp",
        description="When message was created",
    )
    updated_at: datetime.datetime = Field(
        ...,
        title="Updated At Timestamp",
        description="When message was updated",
    )

    generation_id: Optional[str] = Field(
        None,
        title="Generation ID",
        description="Generation ID for the message",
    )

    position: int = Field(
        ...,
        title="Position",
        description="Position in the conversation",
    )
    is_active: bool = Field(
        ...,
        title="Is Active",
        description="Is the message active",
    )

    documents: list[Document] = Field(
        ...,
        title="Documents",
        description="Documents associated with the message",
    )
    citations: list[Citation] = Field(
        ...,
        title="Citations",
        description="Citations associated with the message",
    )
    files: list[ConversationFilePublic] = Field(
        ...,
        title="Files",
        description="Files associated with the message",
    )
    tool_calls: list[ToolCall] = Field(
        ...,
        title="Tool Calls",
        description="Tool calls associated with the message",
    )
    tool_plan: Optional[str] = Field(
        None,
        title="Tool Plan",
        description="Tool plan associated with the message",
    )

    agent: MessageAgent = Field(
        ...,
        title="Agent",
        description="Agent associated with the message",
    )

    class Config:
        from_attributes = True


class UpdateMessage(BaseModel):
    """
    Request to update a message
    """
    text: Optional[str] = Field(
        None,
        title="Text",
        description="The text content of the message",
    )
    title: Optional[str] = Field(
        None,
        title="Title",
        description="The title of the message",
    )

    class Config:
        from_attributes = True
