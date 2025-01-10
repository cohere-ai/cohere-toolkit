import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.schemas.agent import AgentToolMetadata
from backend.schemas.message import Message


class SnapshotAgent(BaseModel):
    """
    Agent Snapshot
    """
    id: str = Field(
        ...,
        title="ID",
        description="Unique identifier for the agent snapshot",
    )
    name: str = Field(
        ...,
        title="Name",
        description="Name of the snapshot",
    )
    description: Optional[str] = Field(
        None,
        title="Description",
        description="Description of the snapshot",
    )
    preamble: Optional[str] = Field(
        None,
        title="Preamble",
        description="Peamble for the snapshot",
    )
    tools_metadata: Optional[list[AgentToolMetadata]] = Field(
        None,
        title="Tools Metadata",
        description="Tools metadata for the snapshot",
    )

    class Config:
        from_attributes = True


class SnapshotData(BaseModel):
    """
    Snapshot data
    """
    title: str = Field(
        ...,
        title="Title",
        description="Title of the snapshot",
    )
    description: str = Field(
        ...,
        title="Description",
        description="Description of the snapshot",
    )
    messages: list[Message] = Field(
        ...,
        title="Messages",
        description="List of messages",
    )
    agent: Optional[SnapshotAgent] = Field(
        None,
        title="Agent",
        description="Agent for the snapshot",
        exclude=True,
    )

    class Config:
        from_attributes = True


class Snapshot(BaseModel):
    """
    Snapshot
    """
    conversation_id: str = Field(
        ...,
        title="Conversation ID",
        description="Unique identifier for the conversation",
    )
    id: str = Field(
        ...,
        title="ID",
        description="Unique identifier for the snapshot",
    )
    last_message_id: str = Field(
        ...,
        title="Last Message ID",
        description="Unique identifier for the last message",
    )
    user_id: str = Field(
        ...,
        title="User ID",
        description="Unique identifier for the user",
    )
    organization_id: Optional[str] = Field(
        None,
        title="Organization ID",
        description="Unique identifier for the organization",
    )

    version: int = Field(
        ...,
        title="Version",
        description="Snapshot version",
    )
    created_at: datetime.datetime = Field(
        ...,
        title="Created At Timestamp",
        description="When snapshot was creted",
    )
    updated_at: datetime.datetime = Field(
        ...,
        title="Updated At Timestamp",
        description="When snapshot was updated",
    )
    snapshot: SnapshotData = Field(
        ...,
        title="Snapshot Data",
        description="Data for the snapshot",
    )
    agent_id: Optional[str] = Field(
        None,
        title="Agent ID",
        description="Unique identifier for the agent",
        exclude=True,
    )

    class Config:
        from_attributes = True


class SnapshotPublic(Snapshot):
    """
    Public snapshot
    """
    user_id: Optional[str] = Field(
        None,
        title="User ID",
        description="Unique identifier for the user",
        exclude=True,
    )
    organization_id: Optional[str] = Field(
        None,
        title="Organization ID",
        description="Unique identifier for the organization",
        exclude=True,
    )

    class Config:
        from_attributes = True


class SnapshotLink(BaseModel):
    """
    Snapshot link
    """
    snapshot_id: str = Field(
        ...,
        title="Snapshot ID",
        description="Unique identifier for the snapshot",
    )
    user_id: str = Field(
        ...,
        title="User ID",
        description="Unique identifier for the user",
    )

    class Config:
        from_attributes = True


class SnapshotLinkPublic(SnapshotLink):
    """
    Public snapshot link
    """
    user_id: Optional[str] = Field(
        None,
        title="User ID",
        description="Unique identifier for the user",
        exclude=True,
    )

    class Config:
        from_attributes = True


class SnapshotAccess(BaseModel):
    """
    Snapshot access
    """
    user_id: str = Field(
        ...,
        title="User ID",
        description="Unique identifier for the user",
    )
    snapshot_id: str = Field(
        ...,
        title="Snapshot ID",
        description="Unique identifier for the snapshot",
    )
    link_id: str = Field(
        ...,
        title="Link ID",
        description="Unique identifier for the link",
    )

    class Config:
        from_attributes = True


class SnapshotWithLinks(SnapshotPublic):
    """
    Snapshot with links
    """
    links: list[str] = Field(
        ...,
        title="Links",
        description="List of links",
    )

    class Config:
        from_attributes = True


class CreateSnapshotRequest(BaseModel):
    """
    Request to create a snapshot
    """
    conversation_id: str = Field(
        ...,
        title="Conversation ID",
        description="Unique identifier for the conversation",
    )

    class Config:
        from_attributes = True


class CreateSnapshotResponse(SnapshotLinkPublic):
    """
    Response for creating a snapshot
    """
    link_id: str = Field(
        ...,
        title="Link ID",
        description="Unique identifier for the link",
    )
    messages: list[Message] = Field(
        ...,
        title="Messages",
        description="List of messages",
    )

    class Config:
        from_attributes = True


class DeleteSnapshotLinkResponse(BaseModel):
    """
    Response for deleting a snapshot link
    """
    pass


class DeleteSnapshotResponse(BaseModel):
    """
    Response for deleting a snapshot
    """
    pass
