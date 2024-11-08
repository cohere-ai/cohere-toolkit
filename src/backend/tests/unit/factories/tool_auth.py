from datetime import datetime

import factory

from backend.config.tools import Tool
from backend.database_models.tool_auth import ToolAuth

from .base import BaseFactory


class ToolAuthFactory(BaseFactory):
    class Meta:
        model = ToolAuth

    user_id = factory.Faker("uuid4")
    tool_id = Tool.Google_Drive.value.ID
    token_type = "Bearer"
    encrypted_access_token = bytes(b"foobar")
    encrypted_refresh_token = bytes(b"foobar")
    expires_at = datetime.strptime("12/31/2124 00:00:00", "%m/%d/%Y %H:%M:%S")
    created_at = datetime.strptime("01/01/2000 00:00:00", "%m/%d/%Y %H:%M:%S")
    updated_at = datetime.strptime("01/01/2010 00:00:00", "%m/%d/%Y %H:%M:%S")
