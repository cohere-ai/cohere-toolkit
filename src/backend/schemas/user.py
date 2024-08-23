import datetime
from typing import Optional

from pydantic import BaseModel

from backend.services.auth import BasicAuthentication

DEFAULT_USER_ID = "user-id"
DEFAULT_USER_NAME = "Default User"


class UserBase(BaseModel):
    fullname: str
    email: Optional[str] = None


class User(UserBase):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class UserPassword(BaseModel):
    password: Optional[str] = None
    hashed_password: Optional[bytes] = None

    def __init__(self, **data):
        password = data.pop("password", None)

        if password is not None:
            data["hashed_password"] = BasicAuthentication.hash_and_salt_password(
                password
            )

        super().__init__(**data)


class CreateUser(UserBase, UserPassword):
    pass


class UpdateUser(UserPassword):
    fullname: Optional[str] = None
    email: Optional[str] = None


class DeleteUser(BaseModel):
    pass
