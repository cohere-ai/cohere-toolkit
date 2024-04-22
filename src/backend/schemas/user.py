import datetime
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    fullname: str
    email: Optional[str] = None


class User(UserBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class CreateUser(UserBase):
    pass


class UpdateUser(UserBase):
    pass


class DeleteUser(BaseModel):
    pass
