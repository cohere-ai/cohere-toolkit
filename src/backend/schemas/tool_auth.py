import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UpdateToolAuth(BaseModel):
    """
    Schema for Tool Authentication
    """
    user_id: Optional[str] = Field(
        None,
        title="User ID",
        description="Unique identifier for the user",
    )
    tool_id: Optional[str] = Field(
        None,
        title="Tool ID",
        description="Unique identifier for the tool",
    )
    token_type: Optional[str] = Field(
        None,
        title="Token Type",
        description="Type of token",
    )
    encrypted_access_token: Optional[bytes] = Field(
        None,
        title="Encrypted Access Token",
        description="Token for authentication",
    )
    encrypted_refresh_token: Optional[bytes] = Field(
        None,
        title="Encrypted Refresh Token",
        description="The token that can be used to refresh the access token",
    )
    expires_at: Optional[datetime.datetime] = Field(
        None,
        title="Expires At",
        description="When the access token expires",
    )

    class Config:
        from_attributes = True
        use_enum_values = True


class DeleteToolAuth(BaseModel):
    """
    Response when deleting a tool auth
    """
    pass
