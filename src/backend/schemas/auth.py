from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field


class Auth(ABC, BaseModel):
    """
    Abstract class for Auth Schemas
    """
    strategy: str = Field(
        ...,
        title="Strategy",
        description="Auth strategy to use",
    )


class Login(Auth):
    """
    Login Request
    """
    payload: Optional[dict[str, str]] = Field(
        None,
        title="Payload",
        description="Login payload depending on strategy used",
    )


class Logout(BaseModel):
    """
    Logout Request
    """
    pass


class ListAuthStrategy(BaseModel):
    """
    List Auth Strategy
    """
    strategy: str = Field(
        ...,
        title="Strategy",
        description="Auth strategy name",
    )
    client_id: Optional[str] = Field(
        None,
        title="Client ID",
        description="Client ID to be used",
    )
    authorization_endpoint: Optional[str] = Field(
        None,
        title="Authorization Endpoint",
        description="The endpoint for authorization",
    )
    pkce_enabled: bool = Field(
        ...,
        title="PKCE Enabled",
        description="If PKCE is enabled",
    )


class JWTResponse(BaseModel):
    """
    JWT Response
    """
    token: str = Field(
        ...,
        title="Token",
        description="JSON Web Token",
    )
