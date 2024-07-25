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


class FilePublic(File):
    user_id: Optional[str] = Field(exclude=True)


class ListFile(FilePublic):
    pass


class UploadFileResponse(FilePublic):
    pass


class DeleteFileResponse(BaseModel):
    pass


class UpdateFileRequest(BaseModel):
    file_name: Optional[str] = None
    message_id: Optional[str] = None

    class Config:
        from_attributes = True
