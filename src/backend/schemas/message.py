import datetime
from typing import List, Union

from pydantic import BaseModel

from backend.database_models.message import MessageAgent
from backend.schemas.citation import Citation
from backend.schemas.document import Document
from backend.schemas.file import File
from backend.schemas.tool import ToolCall


class MessageBase(BaseModel):
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
    tool_calls: List[ToolCall]

    agent: MessageAgent

    class Config:
        from_attributes = True


class UpdateMessage(MessageBase):
    pass
