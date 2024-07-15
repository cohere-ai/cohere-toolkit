from backend.crud import user as user_crud
from backend.database_models.user import User
from backend.schemas.user import DEFAULT_USER_NAME, UpdateUser
from backend.tests.factories import get_factory


def test_create_user(session):
    user_data = User(
        fullname="John Doe",
        email="test@email.com",
    )

    user = user_crud.create_user(session, user_data)
    assert user.fullname == user_data.fullname
    assert user.email == user_data.email

    user = user_crud.get_user(session, user.id)
    assert user.fullname == user_data.fullname
    assert user.email == user_data.email


def test_get_user(session):
    _ = get_factory("User", session).create(id="1", fullname="John Doe")

    user = user_crud.get_user(session, "1")
    assert user.fullname == "John Doe"


def test_fail_get_nonexistent_user(session):
    user = user_crud.get_user(session, "123")
    assert user is None


def test_list_users(session):
    # Delete default users
    session.query(User).delete()
    _ = get_factory("User", session).create(fullname="John Doe")

    users = user_crud.get_users(session)
    assert len(users) == 1
    assert users[0].fullname == "John Doe"


def test_list_users_empty(session):
    # Delete default users
    session.query(User).delete()
    users = user_crud.get_users(session)
    assert len(users) == 0


def test_list_users_with_pagination(session):
    # Delete default users
    session.query(User).delete()
    for i in range(10):
        _ = get_factory("User", session).create(fullname=f"John Doe {i}")

    users = user_crud.get_users(session, offset=5, limit=5)
    assert len(users) == 5


def test_update_user(session):
    user = get_factory("User", session).create(fullname="John Doe")

    new_user_data = UpdateUser(fullname="Jane Doe", email="janedoe@email.com")

    updated_user = user_crud.update_user(session, user, new_user_data)
    assert updated_user.fullname == new_user_data.fullname
    assert updated_user.email == new_user_data.email

    user = user_crud.get_user(session, user.id)
    assert user.fullname == new_user_data.fullname
    assert user.email == new_user_data.email


def test_update_user_partial(session):
    user = get_factory("User", session).create(fullname="John Doe")

    new_user_data = UpdateUser(
        fullname="Jane Doe",
    )

    updated_user = user_crud.update_user(session, user, new_user_data)
    assert updated_user.fullname == new_user_data.fullname
    assert updated_user.email == user.email


def test_donot_update_user(session):
    user = get_factory("User", session).create(fullname="John Doe")

    new_user_data = UpdateUser(fullname="John Doe")

    updated_user = user_crud.update_user(session, user, new_user_data)
    assert updated_user.fullname == user.fullname
    assert updated_user.email == user.email


def test_delete_user(session):
    user = get_factory("User", session).create()

    user_crud.delete_user(session, user.id)

    user = user_crud.get_user(session, user.id)
    assert user is None


def test_delete_nonexistent_user(session):
    user = User(
        fullname="John Doe",
        email="johndoe@email.com",
    )

    user_crud.delete_user(session, user.id)  # no error

    user = user_crud.get_user(session, user.id)
    assert user is None
