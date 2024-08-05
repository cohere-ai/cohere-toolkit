from backend.database_models import Group, User, UserGroupAssociation
from backend.tests.factories import get_factory

from backend.crud import user as user_crud
from backend.crud import group as group_crud


def test_insert_users_into_group(session):
    _ = get_factory("User", session).create(id="1", fullname="John Doe")
    user = user_crud.get_user(session, "1")

    _ = get_factory("Group", session).create(id="1", display_name="Group 1")
    group = group_crud.get_group(session, "1")

    group = group_crud.set_users(session, group, [user])

    assert group.display_name == "Group 1"
    assert group.users == [user]


def test_delete_users_from_group(session):
    test_insert_users_into_group(session)

    group = group_crud.get_group(session, "1")
    group = group_crud.set_users(session, group, [])

    assert group.users == []


def add_one_more_user_to_group(session):
    test_insert_users_into_group(session)

    _ = get_factory("User", session).create(id="2", fullname="Jane Doe")
    user_1 = user_crud.get_user(session, "1")
    user_2 = user_crud.get_user(session, "2")

    group = group_crud.get_group(session, "1")
    group = group_crud.set_users(session, group, [user_1, user_2])

    assert group.users == [user_1, user_2]


def test_replace_users(session):
    test_insert_users_into_group(session)

    _ = get_factory("User", session).create(id="2", fullname="Jane Doe")
    user_2 = user_crud.get_user(session, "2")

    group = group_crud.get_group(session, "1")
    group = group_crud.set_users(session, group, [user_2])

    assert group.users == [user_2]


def test_cascade_group_delete(session):
    test_insert_users_into_group(session)

    group_crud.delete_group(session, "1")

    assert (
        session.query(UserGroupAssociation)
        .filter(UserGroupAssociation.group_id == "1")
        .all()
        == []
    )
