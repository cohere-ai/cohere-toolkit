import datetime
from typing import ClassVar, List, Union

from pydantic import BaseModel

from backend.models.message import MessageAgent, MessageType
from backend.schemas.citation import Citation
from backend.schemas.document import Document
from backend.schemas.file import File


class MessageBase(BaseModel):
    type: ClassVar[MessageType] = MessageType.TEXT
    text: str


class Message(MessageBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    generation_id: Union[str, None]

    position: int
    is_active: bool

    documents: List[Document]
    citations: List[Citation]
    files: List[File]

    agent: MessageAgent
    type: MessageType

    class Config:
        from_attributes = True


class UpdateMessage(MessageBase):
    pass
