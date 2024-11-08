from datetime import datetime

from backend.config.tools import Tool
from backend.crud import tool_auth as tool_auth_crud
from backend.database_models.tool_auth import ToolAuth
from backend.tests.unit.factories import get_factory


def test_create_tool_auth(session, user):
    tool_auth_data = ToolAuth(
        user_id=user.id,
        tool_id=Tool.Google_Drive.value.ID,
        token_type="Bearer",
        encrypted_access_token=bytes(b"foobar"),
        encrypted_refresh_token=bytes(b"foobar"),
        expires_at=datetime.strptime("12/31/2124 00:00:00", "%m/%d/%Y %H:%M:%S"),
        created_at=datetime.strptime("01/01/2000 00:00:00", "%m/%d/%Y %H:%M:%S"),
        updated_at=datetime.strptime("01/01/2010 00:00:00", "%m/%d/%Y %H:%M:%S"),
    )

    tool_auth = tool_auth_crud.create_tool_auth(session, tool_auth_data)

    assert tool_auth.user_id == tool_auth_data.user_id
    assert tool_auth.tool_id == tool_auth_data.tool_id
    assert tool_auth.token_type == tool_auth_data.token_type
    assert tool_auth.encrypted_access_token == tool_auth_data.encrypted_access_token
    assert tool_auth.encrypted_refresh_token == tool_auth_data.encrypted_refresh_token
    assert tool_auth.expires_at == tool_auth_data.expires_at
    assert tool_auth.id == tool_auth_data.id
    assert tool_auth.created_at == tool_auth_data.created_at
    assert tool_auth.updated_at == tool_auth_data.updated_at


def test_delete_tool_auth_by_tool_id(session, user):
    tool_auth = get_factory("ToolAuth", session).create(
        user_id=user.id,
        tool_id=Tool.Google_Drive.value.ID,
        token_type="Bearer",
        encrypted_access_token=bytes(b"foobar"),
        encrypted_refresh_token=bytes(b"foobar"),
        expires_at=datetime.strptime("12/31/2124 00:00:00", "%m/%d/%Y %H:%M:%S"),
        created_at=datetime.strptime("01/01/2000 00:00:00", "%m/%d/%Y %H:%M:%S"),
        updated_at=datetime.strptime("01/01/2010 00:00:00", "%m/%d/%Y %H:%M:%S"),
    )

    tool_auth_crud.delete_tool_auth(session, user.id, tool_auth.tool_id)

    tool_auth = tool_auth_crud.get_tool_auth(session, tool_auth.tool_id, user.id)
    assert tool_auth is None
