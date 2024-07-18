import datetime
from typing import List, Union, Optional

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
    tool_plan: Union[str, None]

    agent: MessageAgent

    class Config:
        from_attributes = True


class UpdateMessage(BaseModel):
    title: Optional[str] = None
    file_ids: Optional[list[str]] = None

    class Config:
        from_attributes = True
