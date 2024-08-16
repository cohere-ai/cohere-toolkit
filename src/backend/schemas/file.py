import datetime
from typing import Optional

from pydantic import BaseModel, Field


class File(BaseModel):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user_id: str
    conversation_id: str
    file_content: str
    file_name: str
    file_path: str
    file_size: int = Field(default=0, ge=0)

    class Config:
        from_attributes = True


class ConversationFilePublic(File):
    user_id: Optional[str] = Field(exclude=True)
    file_content: Optional[str] = Field(exclude=True)


class AgentFilePublic(File):
    user_id: Optional[str] = Field(exclude=True)
    file_content: Optional[str] = Field(exclude=True)
    conversation_id: Optional[str] = Field(exclude=True)


class ListConversationFile(ConversationFilePublic):
    pass


class UploadConversationFileResponse(ConversationFilePublic):
    pass


class UploadAgentFileResponse(AgentFilePublic):
    pass


class DeleteConversationFileResponse(BaseModel):
    pass


class DeleteAgentFileResponse(BaseModel):
    pass
