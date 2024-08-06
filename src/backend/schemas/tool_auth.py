import datetime
from typing import Optional

from pydantic import BaseModel

from backend.services.auth.crypto import decrypt


class ToolAuth(BaseModel):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user_id: str
    tool_id: str
    token_type: str
    encrypted_access_token: bytes
    encrypted_refresh_token: bytes
    expires_at: datetime.datetime

    @property
    def access_token(self) -> str:
        return decrypt(self.encrypted_access_token)

    @property
    def refresh_token(self) -> str:
        return decrypt(self.encrypted_refresh_token)

    class Config:
        from_attributes = True
        use_enum_values = True


class UpdateToolAuth(BaseModel):
    user_id: Optional[str] = None
    tool_id: Optional[str] = None
    token_type: Optional[str] = None
    encrypted_access_token: Optional[bytes] = None
    encrypted_refresh_token: Optional[bytes] = None
    expires_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True
