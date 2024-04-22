import datetime
from typing import Optional

from pydantic import BaseModel, Field


class File(BaseModel):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user_id: str
    conversation_id: str
    file_name: str
    file_path: str
    file_size: int = Field(default=0, ge=0)

    class Config:
        from_attributes = True


class ListFile(File):
    pass


class UploadFile(File):
    pass


class DeleteFile(BaseModel):
    pass


class UpdateFile(BaseModel):
    file_name: Optional[str] = None
    message_id: Optional[str] = None

    class Config:
        from_attributes = True
