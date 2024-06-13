from typing import Optional

from pydantic import BaseModel


class Auth(BaseModel):
    strategy: str


class Login(Auth):
    payload: Optional[dict[str, str]] = None


class Logout(BaseModel):
    pass


class ListAuthStrategy(BaseModel):
    strategy: str


class JWTResponse(BaseModel):
    token: str


class CreateBlacklist(BaseModel):
    token_id: str
