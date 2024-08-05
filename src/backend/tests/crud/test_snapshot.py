import pytest

from backend.crud import snapshot as snapshot_crud
from backend.database_models.snapshot import Snapshot, SnapshotAccess, SnapshotLink
from backend.tests.factories import get_factory

snapshot_json = {
    "title": "Hello, World!",
    "description": "This is a test snapshot.",
}


@pytest.fixture(autouse=True)
def conversation(session, user):
    return get_factory("Conversation", session).create(id="1", user_id=user.id)


@pytest.fixture(autouse=True)
def message(session, conversation, user):
    return get_factory("Message", session).create(
        id="1", conversation_id=conversation.id, user_id=user.id
    )


@pytest.fixture(autouse=True)
def organization(session):
    return get_factory("Organization", session).create(id="1")


@pytest.fixture(autouse=True)
def snapshot(session, conversation, organization, user):
    return get_factory("Snapshot", session).create(
        id="1",
        user_id=user.id,
        organization_id="1",
        conversation_id="1",
        last_message_id="1",
        version=1,
        snapshot=snapshot_json,
    )


@pytest.fixture(autouse=True)
def snapshot_link(session, user):
    return get_factory("SnapshotLink", session).create(
        id="1", snapshot_id="1", user_id=user.id
    )


# Snapshot
def test_create_snapshot(session, user):
    snapshot_data = Snapshot(
        user_id=user.id,
        organization_id="1",
        conversation_id="1",
        last_message_id="1",
        version=1,
        snapshot=snapshot_json,
    )

    snapshot = snapshot_crud.create_snapshot(session, snapshot_data)
    assert snapshot.user_id == snapshot_data.user_id
    assert snapshot.organization_id == snapshot_data.organization_id
    assert snapshot.conversation_id == snapshot_data.conversation_id
    assert snapshot.last_message_id == snapshot_data.last_message_id
    assert snapshot.version == snapshot_data.version
    assert snapshot.snapshot == snapshot_data.snapshot

    snapshot = snapshot_crud.get_snapshot(session, snapshot.id)
    assert snapshot.user_id == snapshot_data.user_id
    assert snapshot.organization_id == snapshot_data.organization_id
    assert snapshot.conversation_id == snapshot_data.conversation_id
    assert snapshot.last_message_id == snapshot_data.last_message_id
    assert snapshot.version == snapshot_data.version
    assert snapshot.snapshot == snapshot_data.snapshot


def test_get_snapshot(session, user):
    snapshot = snapshot_crud.get_snapshot(session, "1")
    assert snapshot.user_id == user.id
    assert snapshot.organization_id == "1"
    assert snapshot.conversation_id == "1"
    assert snapshot.last_message_id == "1"
    assert snapshot.version == 1
    assert snapshot.snapshot == snapshot_json


def test_fail_get_nonexistent_snapshot(session):
    snapshot = snapshot_crud.get_snapshot(session, "123")
    assert snapshot is None


def test_get_snapshot_by_last_message_id(session):
    snapshot = snapshot_crud.get_snapshot_by_last_message_id(session, "1")
    assert snapshot.last_message_id == "1"


def test_fail_get_nonexistent_snapshot_by_last_message_id(session):
    snapshot = snapshot_crud.get_snapshot_by_last_message_id(session, "123")
    assert snapshot is None


def test_list_snapshots(session, user):
    snapshots = snapshot_crud.list_snapshots(session, user.id)
    assert len(snapshots) == 1
    assert snapshots[0].user_id == user.id
    assert snapshots[0].organization_id == "1"
    assert snapshots[0].conversation_id == "1"
    assert snapshots[0].last_message_id == "1"
    assert snapshots[0].version == 1
    assert snapshots[0].snapshot == snapshot_json


def test_fail_list_snapshots(session):
    snapshots = snapshot_crud.list_snapshots(session, "123")
    assert len(snapshots) == 0


def test_delete_snapshot(session, user):
    snapshot_crud.delete_snapshot(session, "1", user.id)

    assert snapshot_crud.get_snapshot(session, "1") is None


# SnapshotLink
def test_create_snapshot_link(session, user):
    snapshot_link_data = SnapshotLink(
        snapshot_id="1",
        user_id=user.id,
    )

    snapshot_link = snapshot_crud.create_snapshot_link(session, snapshot_link_data)
    assert snapshot_link.snapshot_id == snapshot_link_data.snapshot_id

    snapshot_link = snapshot_crud.get_snapshot_link(session, snapshot_link.id)
    assert snapshot_link.snapshot_id == snapshot_link_data.snapshot_id


def test_get_snapshot_link(session):
    snapshot_link = snapshot_crud.get_snapshot_link(session, "1")
    assert snapshot_link.snapshot_id == "1"


def test_fail_get_nonexistent_snapshot_link(session):
    snapshot_link = snapshot_crud.get_snapshot_link(session, "123")
    assert snapshot_link is None


def test_list_snapshot_links(session):
    snapshot_links = snapshot_crud.list_snapshot_links(session, "1")
    assert len(snapshot_links) == 1
    assert snapshot_links[0].snapshot_id == "1"


def test_fail_list_snapshot_links(session):
    snapshot_links = snapshot_crud.list_snapshot_links(session, "123")
    assert len(snapshot_links) == 0


def test_delete_snapshot_link(session, user):
    snapshot_crud.delete_snapshot_link(session, "1", user.id)

    assert snapshot_crud.get_snapshot_link(session, "1") is None


# # SnapshotAccess
def test_create_snapshot_access(session, user):
    snapshot_access_data = SnapshotAccess(
        user_id=user.id,
        snapshot_id="1",
        link_id="1",
    )

    snapshot_access = snapshot_crud.create_snapshot_access(
        session, snapshot_access_data
    )
    assert snapshot_access.user_id == snapshot_access_data.user_id
    assert snapshot_access.snapshot_id == snapshot_access_data.snapshot_id
    assert snapshot_access.link_id == snapshot_access_data.link_id

    snapshot_access = snapshot_crud.get_snapshot_access(session, snapshot_access.id)
    assert snapshot_access.user_id == snapshot_access_data.user_id
    assert snapshot_access.snapshot_id == snapshot_access_data.snapshot_id
    assert snapshot_access.link_id == snapshot_access_data.link_id


def test_get_snapshot_access(session, user):
    _ = get_factory("SnapshotAccess", session).create(
        id="1", user_id=user.id, snapshot_id="1", link_id="1"
    )

    snapshot_access = snapshot_crud.get_snapshot_access(session, "1")
    assert snapshot_access.user_id == user.id
    assert snapshot_access.snapshot_id == "1"
    assert snapshot_access.link_id == "1"


def test_fail_get_nonexistent_snapshot_access(session):
    snapshot_access = snapshot_crud.get_snapshot_access(session, "123")
    assert snapshot_access is None
