from typing import Any

from fastapi import HTTPException

from backend.chat.collate import to_dict
from backend.crud import agent as agent_crud
from backend.crud import conversation as conversation_crud
from backend.crud import snapshot as snapshot_crud
from backend.database_models import Snapshot as SnapshotModel
from backend.database_models import SnapshotAccess as SnapshotAccessModel
from backend.database_models import SnapshotLink as SnapshotLinkModel
from backend.database_models.conversation import Conversation as ConversationModel
from backend.database_models.database import DBSessionDep
from backend.schemas.agent import AgentToolMetadata
from backend.schemas.context import Context
from backend.schemas.conversation import Conversation
from backend.schemas.snapshot import SnapshotAgent, SnapshotData
from backend.services.conversation import get_messages_with_files

SNAPSHOT_VERSION = 1


def validate_last_message(last_message_id: str) -> None:
    if not last_message_id:
        raise HTTPException(status_code=404, detail="Conversation has no messages")


def validate_snapshot_exists(
    session: DBSessionDep, snapshot_id: str, raise_exception: bool = True
) -> SnapshotModel:
    snapshot = snapshot_crud.get_snapshot(session, snapshot_id)
    if not snapshot and raise_exception:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot


def validate_snapshot_link(session: DBSessionDep, link_id: str) -> SnapshotLinkModel:
    snapshot_link = snapshot_crud.get_snapshot_link(session, link_id)
    if not snapshot_link:
        raise HTTPException(status_code=404, detail="Snapshot link not found")

    snapshot = snapshot_crud.get_snapshot(session, snapshot_link.snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    return snapshot


def wrap_create_snapshot_link(
    session: DBSessionDep, snapshot_id: str, user_id: str
) -> SnapshotLinkModel:
    snapshot_link = SnapshotLinkModel(snapshot_id=snapshot_id, user_id=user_id)
    return snapshot_crud.create_snapshot_link(session, snapshot_link)


def wrap_create_snapshot(
    session: DBSessionDep,
    last_message_id: str,
    user_id: str,
    conversation: Conversation,
) -> SnapshotModel:
    snapshot_agent = None
    if conversation.agent_id:
        agent = agent_crud.get_agent_by_id(session, conversation.agent_id, user_id)
        tools_metadata = [to_dict(metadata) for metadata in agent.tools_metadata]

        snapshot_agent = SnapshotAgent(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            preamble=agent.preamble,
            tools_metadata=tools_metadata,
        )

    messages = get_messages_with_files(session, user_id, conversation.messages)
    snapshot_data = SnapshotData(
        title=conversation.title,
        description=conversation.description,
        messages=messages,
        agent=snapshot_agent,
    )
    snapshot = to_dict(snapshot_data)

    snapshot_model = SnapshotModel(
        user_id=user_id,
        organization_id=conversation.organization_id,
        conversation_id=conversation.id,
        last_message_id=last_message_id,
        version=SNAPSHOT_VERSION,
        snapshot=snapshot,
    )
    return snapshot_crud.create_snapshot(session, snapshot_model)


def wrap_create_snapshot_access(
    session: DBSessionDep,
    snapshot_id: str,
    user_id: str,
    link_id: str,
    ctx: Context,
) -> SnapshotAccessModel:
    logger = ctx.get_logger()

    try:
        snapshot_access = SnapshotAccessModel(
            user_id=user_id, snapshot_id=snapshot_id, link_id=link_id
        )
        _ = snapshot_crud.create_snapshot_access(session, snapshot_access)
    except Exception as e:
        # Do not raise exception if snapshot access creation fails
        session.rollback()
        logger.error(event=f"[Snapshot] Error creating snapshot access: {e}")


def remove_private_keys(
    snapshot: dict[str, Any], keys_to_remove: list[str]
) -> dict[str, Any]:
    new_snapshot = remove_keys_nested_dict(snapshot, keys_to_remove)
    return new_snapshot


def remove_keys_nested_dict(d: dict[str, Any], keys_to_remove: list[str]) -> dict:
    if isinstance(d, dict):
        keys = list(d.keys())
        for key in keys:
            if key in keys_to_remove:
                del d[key]
            else:
                d[key] = remove_keys_nested_dict(d[key], keys_to_remove)
    elif isinstance(d, list):
        for i in range(len(d)):
            d[i] = remove_keys_nested_dict(d[i], keys_to_remove)
    return d
