from pydantic import BaseModel


class Login(BaseModel):
    strategy: str
    payload: dict[str, str]

    class Config:
        from_attributes = True
