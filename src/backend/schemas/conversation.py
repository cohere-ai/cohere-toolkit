import datetime
from typing import List, Union, Optional

from pydantic import BaseModel, computed_field, Field

from backend.schemas.message import Message
from backend.schemas.file import File


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
