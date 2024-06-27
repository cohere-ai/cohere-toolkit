import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from backend.chat.collate import to_dict
from backend.config.routers import RouterName
from backend.crud import conversation as conversation_crud
from backend.crud import snapshot as snapshot_crud
from backend.database_models import Snapshot as SnapshotModel
from backend.database_models import SnapshotAccess as SnapshotAccessModel
from backend.database_models import SnapshotLink as SnapshotLinkModel
from backend.database_models.database import DBSessionDep
from backend.schemas.snapshot import (
    CreateSnapshot,
    CreateSnapshotResponse,
    Snapshot,
    SnapshotAccess,
    SnapshotLink,
)

SNAPSHOT_VERSION = 1


def validate_conversation(session, conversation_id, user_id):
    conversation = conversation_crud.get_conversation(session, conversation_id, user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


def validate_last_message(last_message_id):
    if not last_message_id:
        raise HTTPException(status_code=404, detail="Conversation has no messages")


def validate_snapshot_doest_exist(session, last_message_id):
    snapshot = snapshot_crud.get_snapshot_by_last_message_id(session, last_message_id)
    if snapshot:
        raise HTTPException(status_code=409, detail="Snapshot already exists")
    return snapshot


def validate_snapshot_exists(session, snapshot_id):
    snapshot = snapshot_crud.get_snapshot(session, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot


def validate_snapshot_link(session, link_id):
    snapshot_link = snapshot_crud.get_snapshot_link(session, link_id)
    if not snapshot_link:
        raise HTTPException(status_code=404, detail="Snapshot link not found")

    snapshot = snapshot_crud.get_snapshot(session, snapshot_link.snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")

    return snapshot


def create_conversation_dict(conversation):
    try:
        conversation_dict = to_dict(conversation)
        conversation_dict["messages"] = to_dict(conversation.messages)
        conversation_dict.pop("text_messages", None)
        return conversation_dict
    except Exception as e:
        logging.error(f"Error creating snapshot: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating snapshot - {e}")


def wrap_create_snapshot_link(session, snapshot_id, user_id):
    snapshot_link = SnapshotLinkModel(snapshot_id=snapshot_id, user_id=user_id)
    return snapshot_crud.create_snapshot_link(session, snapshot_link)


def wrap_create_snapshot(session, last_message_id, user_id, conversation_dict):
    snapshot_model = SnapshotModel(
        user_id=user_id,
        organization_id=conversation_dict.get("organization_id"),
        conversation_id=conversation_dict.get("id"),
        last_message_id=last_message_id,
        version=SNAPSHOT_VERSION,
        snapshot=conversation_dict,
    )
    return snapshot_crud.create_snapshot(session, snapshot_model)


def wrap_create_snapshot_access(session, snapshot_id, user_id, link_id):
    try:
        snapshot_access = SnapshotAccessModel(
            user_id=user_id, snapshot_id=snapshot_id, link_id=link_id
        )
        _ = snapshot_crud.create_snapshot_access(session, snapshot_access)
    except Exception as e:
        # Do not raise exception if snapshot access creation fails
        session.rollback()
        logging.error(f"Error creating snapshot access: {e}")


def remove_private_keys(snapshot, keys_to_remove: list[str]):
    new_snapshot = remove_keys_nested_dict(snapshot, keys_to_remove)
    return new_snapshot


def remove_keys_nested_dict(d, keys_to_remove: list[str]) -> dict:
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
