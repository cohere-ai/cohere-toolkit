import datetime
from typing import List, Optional

from pydantic import BaseModel

from backend.schemas.message import Message


class SnapshotBase(BaseModel):
    user_id: str
    organization_id: str
    conversation_id: str
    last_message_id: str
    version: int


class Snapshot(SnapshotBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    messages: List[Message]
    description: Optional[str]
    title: str

    class Config:
        from_attributes = True


class SnapshotLink(BaseModel):
    snapshot_id: str

    class Config:
        from_attributes = True


class SnapshotAccess(BaseModel):
    user_id: str
    snapshot_id: str
    link_id: str

    class Config:
        from_attributes = True
