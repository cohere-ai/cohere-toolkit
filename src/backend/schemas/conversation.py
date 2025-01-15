import datetime
from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field, computed_field

from backend.schemas.file import ConversationFilePublic
from backend.schemas.message import Message


class ConversationBase(ABC, BaseModel):
    """
    Abstract class for Conversation Schemas
    """
    user_id: str = Field(
        ...,
        title="User ID",
        description="User ID for the conversation",
    )
    organization_id: Optional[str] = Field(
        None,
        title="Organization ID",
        description="Organization ID for the conversation",
    )


class Conversation(ConversationBase):
    """
    Schema for a conversation
    """
    id: str = Field(
        ...,
        title="ID",
        description="Unique identifier for the conversation",
    )
    created_at: datetime.datetime = Field(
        ...,
        title="Created At Timestamp",
        description="When the conversation was created",
    )
    updated_at: datetime.datetime = Field(
        ...,
        title="Updated At Timestamp",
        description="When the conversation was updated",
    )

    title: str = Field(
        ...,
        title="Title",
        description="Title of the conversation",
    )
    messages: list[Message] = Field(
        ...,
        title="Messages",
        description="The conversation messages",
    )
    files: list[ConversationFilePublic] = Field(
        ...,
        title="Files",
        description="List of files for the conversation",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Description of the conversation",
    )
    agent_id: Optional[str] = Field(
        None,
        title="Agent ID",
        description="Unique identifier for the agent used in the conversation",
    )
    is_pinned: bool = Field(
        ...,
        title="Is Pinned",
        description="If conversation is pinned",
    )

    @computed_field(return_type=int)
    def total_file_size(self):
        return sum([getattr(file, "file_size", 0) for file in self.files])

    class Config:
        from_attributes = True


class ConversationPublic(Conversation):
    """
    A public conversation which removes the User ID and Organization ID
    """
    user_id: Optional[str] = Field(
        exclude=True,
        title="User ID",
        description="User ID for the conversation",
    )
    organization_id: Optional[str] = Field(
        exclude=True,
        title="Organization ID",
        description="Organization ID for the conversation",
    )


class ConversationWithoutMessages(ConversationPublic):
    """
    A public conversation without messages attached
    """
    messages: list[Message] = Field(
        exclude=True,
        title="Messages",
        description="The conversation messages",
    )


class UpdateConversationRequest(BaseModel):
    """
    Request to update a conversation
    """
    title: Optional[str] = Field(
        None,
        title="Title",
        description="Title of the conversation",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Description of the conversation",
    )

    class Config:
        from_attributes = True


class ToggleConversationPinRequest(BaseModel):
    """
    Request to toggle pinning a conversation
    """
    is_pinned: bool = Field(
        ...,
        title="Is Pinned",
        description="If conversation is pinned",
    )


class DeleteConversationResponse(BaseModel):
    """
    Response for deleting a conversation
    """
    pass


class GenerateTitleResponse(BaseModel):
    """
    Response for generating a title
    """
    title: str = Field(
        ...,
        title="Title",
        description="Title generated for the conversation",
    )
    error: Optional[str] = Field(
        None,
        title="Error",
        description="Error message if the response is an error",
    )
