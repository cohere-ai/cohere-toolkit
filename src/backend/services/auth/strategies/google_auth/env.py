from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleAuthEnvironment(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    google_client_id: str = Field(min_length=1)
    google_client_secret: str = Field(min_length=1)
    frontend_hostname: str = Field(min_length=1)
