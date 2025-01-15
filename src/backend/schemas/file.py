import datetime
from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field


class FileBase(ABC, BaseModel):
    """
    Abstract class for File schemas
    """
    id: str = Field(
        ...,
        title="ID",
        description="Unique identifier of the file",
    )
    created_at: datetime.datetime = Field(
        ...,
        title="Created At Timestamp",
        description="When file was created",
    )
    updated_at: datetime.datetime = Field(
        ...,
        title="Updated At Timestamp",
        description="When file was updated",
    )
    file_name: str = Field(
        ...,
        title="File Name",
        description="Name of the file",
    )
    file_size: int = Field(
        0,
        title="File Size",
        description="Size of the file in bytes",
        ge=0
    )



class File(FileBase):
    """
    Schema for a File
    """
    user_id: str = Field(
        ...,
        title="User ID",
        description="Unique identifier for who created the file",
    )
    conversation_id: Optional[str] = Field(
        "",
        title="Conversation ID",
        description="Unique identifier for the conversation the file is associated to",
    )
    file_content: Optional[str] = Field(
        "",
        title="File Content",
        description="The contents of the file",
    )

    class Config:
        from_attributes = True


class ConversationFilePublic(FileBase):
    """
    Schema for a public conversation file
    """
    user_id: str = Field(
        ...,
        title="User ID",
        description="Unique identifier for who created the file",
    )
    conversation_id: str = Field(
        ...,
        title="Conversation ID",
        description="Unique identifier for the conversation the file is associated to",
    )


class AgentFilePublic(FileBase):
    """
    Schema for a public agent file
    """
    pass


class FileMetadata(FileBase):
    """
    Schema for file metadata
    """
    file_content: str = Field(
        ...,
        title="File Content",
        description="The contents of the file",
    )


class ListConversationFile(ConversationFilePublic):
    """
    Listing conversation files
    """
    pass


class UploadConversationFileResponse(ConversationFilePublic):
    """
    Response for uploading a conversation file
    """
    pass


class UploadAgentFileResponse(AgentFilePublic):
    """
    Reponse for uploading an agent file
    """
    pass


class DeleteConversationFileResponse(BaseModel):
    """
    Response for deleting a conversation file
    """
    pass


class DeleteAgentFileResponse(BaseModel):
    """
    Response for deleting an agent file
    """
    pass
