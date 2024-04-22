import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, computed_field

from backend.schemas.file import File
from backend.schemas.message import Message


class ConversationBase(BaseModel):
    user_id: str


class Conversation(ConversationBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    title: str
    messages: List[Message]
    files: List[File]
    description: Optional[str]

    @computed_field(return_type=int)
    def total_file_size(self):
        return sum([getattr(file, "file_size", 0) for file in self.files])

    class Config:
        from_attributes = True


class ConversationWithoutMessages(Conversation):
    messages: List[Message] = Field(exclude=True)


class UpdateConversation(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class DeleteConversation(BaseModel):
    pass
