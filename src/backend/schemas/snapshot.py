import datetime
from typing import Union

from pydantic import BaseModel


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
