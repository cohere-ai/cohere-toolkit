import datetime
from typing import Optional

from pydantic import BaseModel, Field


class File(BaseModel):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user_id: str
    conversation_id: Optional[str] = ""
    file_content: Optional[str] = ""
    file_name: str
    file_size: int = Field(default=0, ge=0)

    class Config:
        from_attributes = True


class ConversationFilePublic(BaseModel):
    id: str
    user_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    conversation_id: str
    file_name: str
    file_size: int = Field(default=0, ge=0)



class AgentFilePublic(BaseModel):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    file_name: str
    file_size: int = Field(default=0, ge=0)

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
