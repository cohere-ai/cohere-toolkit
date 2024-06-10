import datetime
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


class JWTToken(BaseModel):
    iss: str
    iat: datetime.datetime
    exp: datetime.datetime
    jti: str
    context: dict


class JWTResponse(BaseModel):
    token: JWTToken

class CreateBlacklist(BaseModel):
    token_id: str