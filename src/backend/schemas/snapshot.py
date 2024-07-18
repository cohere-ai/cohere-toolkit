import datetime
from typing import Optional, Union

from pydantic import BaseModel

from backend.schemas.agent import AgentToolMetadata
from backend.schemas.message import Message


class SnapshotAgent(BaseModel):
    id: str
    name: str
    description: Optional[str]
    preamble: Optional[str]
    tools_metadata: Optional[list[AgentToolMetadata]]

    class Config:
        from_attributes = True


class SnapshotData(BaseModel):
    title: str
    description: str
    messages: list[Message]
    agent: Optional[SnapshotAgent]

    class Config:
        from_attributes = True


class Snapshot(BaseModel):
    conversation_id: str
    id: str
    last_message_id: str
    user_id: str
    organization_id: Union[str, None]

    version: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    snapshot: SnapshotData

    class Config:
        from_attributes = True


class SnapshotLink(BaseModel):
    snapshot_id: str
    user_id: str

    class Config:
        from_attributes = True


class SnapshotAccess(BaseModel):
    user_id: str
    snapshot_id: str
    link_id: str

    class Config:
        from_attributes = True


class SnapshotWithLinks(Snapshot):
    links: list[str]

    class Config:
        from_attributes = True


class CreateSnapshot(BaseModel):
    conversation_id: str

    class Config:
        from_attributes = True


class CreateSnapshotResponse(SnapshotLink):
    link_id: str
    messages: list[Message]

    class Config:
        from_attributes = True
