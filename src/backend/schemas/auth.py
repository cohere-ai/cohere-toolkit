from typing import Optional

from pydantic import BaseModel


class Auth(BaseModel):
    strategy: str


class Login(Auth):
    payload: Optional[dict[str, str]] = None
