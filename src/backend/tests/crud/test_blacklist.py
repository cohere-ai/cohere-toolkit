import uuid

from backend.crud import blacklist as blacklist_crud
from backend.database_models.blacklist import Blacklist
from backend.tests.factories import get_factory


def test_create_blacklist(session):
    token_id = str(uuid.uuid4())
    blacklist_data = Blacklist(token_id=token_id)
    blacklist = blacklist_crud.create_blacklist(session, blacklist_data)

    blacklist = session.query(Blacklist).filter(Blacklist.token_id == token_id).first()

    assert blacklist is not None
    assert blacklist.token_id == token_id


def test_get_blacklist(session):
    token_id = str(uuid.uuid4())

    _ = get_factory("Blacklist", session).create(token_id=token_id)

    blacklist = blacklist_crud.get_blacklist(session, token_id)
    assert blacklist is not None
    assert blacklist.token_id == token_id


def test_fail_get_nonexistent_blacklist(session):
    blacklist = blacklist_crud.get_blacklist(session, "123")
    assert blacklist is None
