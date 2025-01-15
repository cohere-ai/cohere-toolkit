import datetime
from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field

from backend.services.auth import BasicAuthentication

DEFAULT_USER_ID = "user-id"
DEFAULT_USER_NAME = "Default User"


class UserBase(ABC, BaseModel):
    """
    Abstract class for User Schemas
    """
    fullname: str = Field(
        ...,
        title="Full Name",
        description="User's Full Name",
    )
    email: Optional[str] = Field(
        None,
        title="Email",
        description="User's email address",
    )


class User(UserBase):
    """
    User schema
    """
    id: str = Field(
        ...,
        title="ID",
        description="",
    )
    created_at: datetime.datetime = Field(
        ...,
        title="Created At Timestamp",
        description="When the user was created",
    )
    updated_at: datetime.datetime = Field(
        ...,
        title="Updated At Timestamp",
        description="When the user was updated",
    )

    class Config:
        from_attributes = True


class UserPassword(ABC, BaseModel):
    """
    Adstract class for user schemas
    """
    password: Optional[str] = Field(
        None,
        title="Password",
        description="Password for the user",
    )
    hashed_password: Optional[bytes] = Field(
        None,
        title="Hashed Password",
        description="The user's password hashed",
    )

    def __init__(self, **data):
        password = data.pop("password", None)

        if password is not None:
            data["hashed_password"] = BasicAuthentication.hash_and_salt_password(
                password
            )

        super().__init__(**data)


class CreateUser(UserBase, UserPassword):
    """
    Request to create a user
    """
    pass


class UpdateUser(UserPassword):
    """
    Request to update a user
    """
    fullname: Optional[str] = Field(
        None,
        title="Full Name",
        description="User's Full Name",
    )
    email: Optional[str] = Field(
        None,
        title="Email",
        description="User's email address",
    )


class DeleteUser(BaseModel):
    """
    Response when deleting a user
    """
    pass
