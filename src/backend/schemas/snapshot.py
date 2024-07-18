import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field

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
    agent: Optional[SnapshotAgent] = Field(exclude=True)

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


class SnapshotPublic(Snapshot):
    user_id: Optional[str] = Field(exclude=True)
    organization_id: Optional[str] = Field(exclude=True)

    class Config:
        from_attributes = True


class SnapshotLink(BaseModel):
    snapshot_id: str
    user_id: str

    class Config:
        from_attributes = True


class SnapshotLinkPublic(SnapshotLink):
    user_id: Optional[str] = Field(exclude=True)

    class Config:
        from_attributes = True


class SnapshotAccess(BaseModel):
    user_id: str
    snapshot_id: str
    link_id: str

    class Config:
        from_attributes = True


class SnapshotWithLinks(SnapshotPublic):
    links: list[str]

    class Config:
        from_attributes = True


class CreateSnapshotRequest(BaseModel):
    conversation_id: str

    class Config:
        from_attributes = True


class CreateSnapshotResponse(SnapshotLinkPublic):
    link_id: str
    messages: list[Message]

    class Config:
        from_attributes = True


class DeleteSnapshotLinkResponse(BaseModel):
    pass


class DeleteSnapshotResponse(BaseModel):
    pass
