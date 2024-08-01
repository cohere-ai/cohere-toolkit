import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, computed_field

from backend.schemas.file import File
from backend.schemas.message import Message


class ConversationBase(BaseModel):
    user_id: str
    organization_id: Optional[str] = None


class Conversation(ConversationBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    title: str
    messages: List[Message]
    files: List[File]
    description: Optional[str]
    agent_id: Optional[str]

    @computed_field(return_type=int)
    def total_file_size(self):
        return sum([getattr(file, "file_size", 0) for file in self.files])

    class Config:
        from_attributes = True


class ConversationPublic(Conversation):
    user_id: Optional[str] = Field(exclude=True)
    organization_id: Optional[str] = Field(exclude=True)


class ConversationWithoutMessages(ConversationPublic):
    messages: List[Message] = Field(exclude=True)


class UpdateConversationRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class DeleteConversationResponse(BaseModel):
    pass


class GenerateTitleResponse(BaseModel):
    title: str
