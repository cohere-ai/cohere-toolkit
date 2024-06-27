import datetime
from typing import Optional

from pydantic import BaseModel


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
