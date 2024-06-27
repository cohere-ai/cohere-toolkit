import datetime
from typing import Union

from pydantic import BaseModel


class Snapshot(BaseModel):
    conversation_id: str
    id: str
    last_message_id: str
    user_id: str
    organization_id: Union[str, None]

    version: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    snapshot: Union[dict, None]

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
    messages: list[dict]

    class Config:
        from_attributes = True
